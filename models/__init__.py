from __future__ import division
import datetime
from PIL import Image as PIL_Image

from django.db import models
from django.conf import settings
from django.core.files.storage import FileSystemStorage

from webhelpers.html.tags import image
from editsite.util import puff

# These will be options in the admin sec when editing layouts
active_fields = [
    'TextField',
    'ImageField',
    'PopupImageField',
    'ImageListField',
    'ListImage'
]

class BaseTable(models.Model):

    class Meta:
        app_label = 'editsite'
        abstract = True

    def __unicode__(self):
        l = []
        for name in self._meta.get_all_field_names():
            try:
                l.append(u'%s: %s' %(name, unicode(self.__getattribute__(name))))
            except self.__class__.DoesNotExist, e:
                pass
        return u'; '.join(l)

# Independents (nothing to do with page heirarchy)
class Image(BaseTable):
    file = models.ImageField(upload_to="images", help_text="upload an image file")
    alt = models.CharField(max_length=63, help_text="Short description of the image, displays when image doesnt load (not normally visible, but required by HTML standards and can help with SEO)", null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True, help_text="Description that appears on mouse over")
    width = models.IntegerField(help_text="width in pixels", null=True, blank=True)
    height = models.IntegerField(help_text="height in pixels", null=True, blank=True)
    format = models.CharField(max_length=7, null=True, blank=True)

    def __unicode__(self):
        return unicode(self.file)

    @property
    def absolute_url(self):
        return self.file.url

    def save(self, *args, **kwargs):
        if not self.format:
            self.format = self._get_format()
        super(Image, self).save(*args, **kwargs)
        if self.width or self.height:
            self.resize(width=self.width, height=self.height, save=True)

    def delete(self, *args, **kwargs):
        if len(Image.objects.filter(file=self.file)) == 1:
            self.file.delete(save=False)
        return super(Image, self).delete(*args, **kwargs)

    def _get_format(self):
        import os.path
        name, ext = os.path.splitext(self.file.name)
        ext = ext[1:]
        if ext in (u'jpg',u'JPG',u'jpeg',u'JPEG'):
            return u'JPEG'
        if ext in (u'png',u'PNG'):
            return u'PNG'
        if ext in (u'gif',u'GIF'):
            return u'GIF'
        if ext in (u'bmp',u'BMP'):
            return u'BMP'
        raise TypeError('Image Format not supported')

    def resize(self, width=None, height=None, save=True):
        im = PIL_Image.open(self.file.path)
        w = width or im.size[0]
        h = height or im.size[1]
        w_r = w/im.size[0]
        h_r = h/im.size[1]
        if (w_r < h_r):
            h = int(round(w_r * im.size[1]))
        else:
            w = int(round(h_r * im.size[0]))
        if (im.mode != 'RGB'):
            im = im.convert('RGB')
        if w == im.size[0] and h == im.size[1]:
            return
        im = im.resize((w,h), PIL_Image.ANTIALIAS)
        im.save(self.file.path, quality=95)
        self.width = w
        self.height = h
        if save:
            super(Image, self).save()

# Page Heirarchy
class Layout(BaseTable):
    name = models.CharField(max_length=255)
    template = models.CharField(max_length=63)
    has_menu = models.BooleanField(default=True, help_text="whether the menu is in this layout (for optimization purposes)")

    class Meta:
        app_label = 'editsite'

    def __unicode__(self):
        return self.name

class Page(BaseTable):
    name = models.CharField(max_length=63, unique=True, help_text='For internal identification purposes only -- not displayed to user (must be unique)')
    title_en = models.CharField(max_length=63, null=True, blank=True, verbose_name="English Title")
    title_es = models.CharField(max_length=63, null=True, blank=True, verbose_name="Spanish Title")
    title_de = models.CharField(max_length=63, null=True, blank=True, verbose_name="German Title")
    title_fr = models.CharField(max_length=63, null=True, blank=True, verbose_name="French Title")
    uri = models.CharField(max_length=255, unique=True, help_text="end of url for this page -- full url will be http://www.machupicchuinformation.com/URI UNLESS layout is external, in which case this is the full url (must be unique)")
    parent = models.ForeignKey("self", related_name="children", help_text="parent page on menu", null=True, blank=True)
    on_menu = models.BooleanField(default=True, help_text="whether this page appears on the menu")
    menu_order = models.IntegerField(default=0, help_text="pages are ordered on the menu wrt this field, doesn't have to be sequential")
    layout = models.ForeignKey(Layout, help_text="layout of the page. Choose external to represent external pages (e.g. http://www.google.com/) on the menu", on_delete="SET_NULL")
    accessable = models.BooleanField(default=True, help_text="Turn this off if you want to deny access to this page (useful for unaccessable parents or for saving pages that are not ready to be published)")
    date_published = models.DateField(default=datetime.date.today, help_text="Publish date -- not currently displayed to user")

    class Meta:
        app_label = 'editsite'

    def __unicode__(self):
        return self.name

    def clear_fields(self):
        pass

    @property
    def parents(self):
        return [p for p in self.xparents()]

    def xparents(self):
        page = self
        while page.parent:
            yield page.parent
            page = page.parent

    @property
    def all_children(self):
        return [c for c in self.xall_children()]

    def xall_children(self):
        for child in self.children.all():
            yield child
            for c in child.xall_children():
                yield c

    @property
    def fields(self):
        return [f for f in self.xfields()]

    def xfields(self):
        for input in self.layout.inputs.all():
            try:
                yield input.field_model.objects.get(input=input, page=self)
            except (input.field_model.DoesNotExist):
                pass

    def get_field_by_input_name(self, name):
        input = Input.objects.get(name=name, layout=self.layout)
        return input.field_model.objects.get(input=input, page=self)

# These will be options in the admin sec when editing layouts
active_fields = [
    'TextField',
    'ImageField',
    'PopupImageField',
    'ImageListField',
    'ListImage'
]

# Input (maps Layouts to Fields)
class Input(BaseTable):
    field_class = models.CharField(max_length=63, choices=puff(active_fields), help_text="The Table Used for storing the user input and rendering")
    help_text = models.CharField(max_length=255, null=True, blank=True, help_text="Help text to display to admin about this input")
    name = models.CharField(max_length=63, help_text="Name to display to the admin")
    varname = models.CharField(max_length=63, help_text="Variable name for use in templates")
    layout = models.ForeignKey(Layout, related_name="inputs")

    class Meta:
        app_label = 'editsite'

    def __init__(self, *args, **kwargs):
        self._field_model = None
        super(Input, self).__init__(*args, **kwargs)

    def __unicode__(self):
        return u'%s: %s' %(self.layout.name, self.field_class)

    @property
    def field_model(self):
        if self._field_model is None:
            if self.field_class in active_fields:
                self._field_model = eval(self.field_class)
            else:
                raise NameError('Invalid Field Class: %s' %(self.field_class))
        return self._field_model

# Abstract Classes
class _Image(Image):

    class Meta:
        abstract = True
        app_label = 'editsite'

    def render(self, **attrs):
        return image(self.url, self.alt, title=self.title, **attrs)

class _Field(BaseTable):
    page = models.ForeignKey(Page, null=True, blank=True, related_name="%(app_label)s_%(class)s", editable=False) #it's only null and blank b/c we save these b4 the page
    input = models.ForeignKey(Input, related_name="%(app_label)s_%(class)s", editable=False)

    class Meta:
        abstract = True
        app_label = 'editsite'

    def render(self):
        raise NotImplementedError()

# Fields (Append new to the bottom or wherever)
class TextField(_Field):
    text_en = models.TextField(help_text="English Text")
    text_es = models.TextField(help_text="Spanish Text", null=True, blank=True)
    text_de = models.TextField(help_text="German Text", null=True, blank=True)
    text_fr = models.TextField(help_text="French Text", null=True, blank=True)

    class Meta:
        app_label = 'editsite'

    def render(self, lang=None):
        if lang and self.__getattribute__('text_%s' %lang):
            return self.__getattribute__('text_%s' %lang)
        return self.__getattribute__('text_en')

class ImageField(_Field, _Image):
    class Meta:
        app_label = 'editsite'

class PopupImageField(_Field, _Image):
    thumbnail_file = models.FileField(upload_to='thumbs')

    class Meta:
        app_label = 'editsite'

    def render(self, class_='popup', **attrs):
        return _Image.render(self, class_, **attrs)

class ImageListField(_Field):

    class Meta:
        app_label = 'editsite'

    def render(self):
        pass

class ListImage(_Image):
    image_list = models.ForeignKey(ImageListField)

    class Meta:
        app_label = 'editsite'
