from django import forms
from django.contrib import admin
from django.db import models
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from django.conf.urls.defaults import patterns
from django.forms.forms import BoundField
from django.forms.models import model_to_dict

from editsite.forms.admin import PageForm, ImageForm
from editsite.helpers import InputFieldset, make_safe_input_name, get_data_with_prefix
from editsite.models import Page, Layout, Input, Image
from editsite.widgets import EditsiteHtmlEditorWidget

class ImageAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['file','alt','title']}),
        ('Photo Resizing', {
            'fields': [('width', 'height')],
            'description': 'The image will never be distorted, so if both width and height are provided the most constraining one will take effect'
        }),
        ('Advanced', {
            'fields': ['format'],
            'classes': ['collapse']
        })
    ]

    form = ImageForm
    actions = ['delete_selected']

    def delete_selected(self, request, queryset):
        for image in queryset.all():
            image.delete()
    delete_selected.short_description = 'Delete Selected Images'



class PageAdmin(admin.ModelAdmin):
    class Media:
        js = (
            "js/jquery-1.6.2.min.js",
            "js/tinymce/tiny_mce.js",
            "js/page_change_form.js"
        )
        css = {
            'all': ('css/forms.css',)
        }

    form = PageForm
    list_display = ('name', 'uri', 'layout', 'parent', 'menu_order')
    list_filter = ('date_published', 'parent', 'layout')
    list_editable = ('uri', 'menu_order')
    search_fields = ('name', 'uri', 'title_en', 'editsite_textfield__text_en')
    date_heirarchy = 'date_published'
    fieldsets = [
        (None, {'fields': ['name']}),
        ('Title', {
            'fields': [('title_en', 'title_es'), ('title_de', 'title_fr')],
            'description': "Title that appears in the user's browser tab"
        }),
        (None, {'fields': ['uri', ('on_menu', 'parent'), 'menu_order', 'layout']}),
        ('Advanced', {
            'fields': ['date_published', 'accessable'],
            'classes': ['collapse']
        })
    ]
    formfield_overrides = {
        models.TextField: {'widget': EditsiteHtmlEditorWidget},
    }
    save_on_top = True

    def get_urls(self):
        urls = super(PageAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^layout', self.admin_site.admin_view(self.layout_view)),
            (r'^image_list', self.admin_site.admin_view(self.image_list_view))
        )
        return my_urls + urls

    def image_list_view(self, request):
        import os.path
        def make_image_name(filename):
            d, f = os.path.split(filename)
            if d == 'thumbs':
                return u'Thumbnail: %s' %f
            return f

        images = Image.objects.all()
        image_names = []
        for image in images:
            image_names.append(
                u'["%s", "/media/user/%s"]' %(make_image_name(image.file.name), image.file.name)
            )
        return HttpResponse(
            u'var tinyMCEImageList = new Array(%s);' %u','.join(image_names),
            content_type = 'text/javascript'
        )

    def layout_view(self, request):
        layout_id = request.POST['layout_id']
        layout = get_object_or_404(Layout, pk=layout_id)
        inits = {}
        if request.POST.get('page_id'):
            try:
                page = Page.objects.get(pk=request.POST['page_id'])
                for field in page.xfields():
                    for name, value in model_to_dict(field, exclude=('input','page')).iteritems():
                        inits['%s-%s' %(make_safe_input_name(field.input.name), name)] = value
            except (Page.DoesNotExist, Layout.DoesNotExist):
                pass
        ModelForm = self.get_form(request)
        inputs = []
        for input in layout.inputs.all():
            fields = []
            prefix = make_safe_input_name(input.name)
            data = get_data_with_prefix(inits, prefix)
            form = ModelForm(initial=data, prefix=prefix)
            for field in input.field_model._meta.fields:
                if field.editable:
                    formfield = self.formfield_for_dbfield(field, request=request)
                    if formfield is not None:
                        fields.append(BoundField(form, formfield, field.name))
            inputs.append(InputFieldset(input, fields))
        return render_to_response('admin/editsite/page/layout_inputs.html', {'inputs': inputs, 'layout': layout})

class InputInline(admin.TabularInline):
    model = Input
    extra = 3
    fields = ['field_class', 'name', 'varname', 'help_text']

class LayoutAdmin(admin.ModelAdmin):
    inlines = [InputInline]

admin.site.register(Page, PageAdmin)
admin.site.register(Layout, LayoutAdmin)
admin.site.register(Image, ImageAdmin)
