from django.forms import ModelForm
from django.forms.models import modelform_factory
from django.conf import settings
from django.core.exceptions import ValidationError

from editsite.forms.forms import GeneralForm
from editsite.models import Page, Image
from editsite.helpers import make_safe_input_name, get_data_with_prefix, resize_image

class PageForm(ModelForm):
    class Meta:
        model = Page

    def __init__(self, *args, **kwargs):
        self.layout_fields = kwargs.pop('layout_fields', {})
        super(PageForm, self).__init__(*args, **kwargs)

    def clean(self):
        self.cleaned_data = ModelForm.clean(self)
        self.instance.clear_fields()
        for input in self.cleaned_data['layout'].inputs.all():
            all_data = self.data.copy()
            all_data.update(self.files)
            data = get_data_with_prefix(all_data, make_safe_input_name(input.name))
            field = input.field_model(input=input, **data)
            # field.page = self.instance
            try:
                field.full_clean()
            except ValidationError, e:
                # we should handle this
                raise e
            #field.save()
            self.layout_fields.setdefault('%s_%s' %(input.field_model._meta.app_label, input.field_model.__name__.lower()),[]).append(field)
        return self.cleaned_data

    def save(self, commit=True):
        page = super(PageForm, self).save(True)
        for key, val in self.layout_fields.iteritems():
            page.__setattr__(key, val)
        page.save()
        return page

    def save_m2m(self):
        pass

class ImageForm(ModelForm):
    class Meta:
        model = Image

    #def save(self, commit=True):
    #    image = super(ImageForm, self).save(commit)
    #    if self.cleaned_data['width'] or self.cleaned_data['height']:
    #        import threading
    #        t = threading.Thread(None, target=resize_image,
    #                             args=('%simages/%s' %(settings.MEDIA_ROOT, image.file.name),),
    #                             kwargs={
    #                                'width': self.cleaned_data['width'],
    #                                'height': self.cleaned_data['height']
    #                             })
    #        t.start()
    #    return image
