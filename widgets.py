from django.contrib.admin.widgets import AdminTextareaWidget
from django.conf import settings

MEDIA_FOLDER = settings.EDITSITE_MEDIA_PREFIX

class EditsiteHtmlEditorWidget(AdminTextareaWidget):
    class Media:
        js = (MEDIA_FOLDER + 'js/tiny_mce/jquery.tinymce.js',
              MEDIA_FOLDER + 'js/widgets.js')

    def __init__(self, attrs={}):
        final_attrs = {'class': 'vLargeTextField tinymce', 'cols': '80', 'rows': '20'}
        final_attrs.update(attrs)
        super(AdminTextareaWidget, self).__init__(attrs=final_attrs)

class Htmli18nEditor(EditsiteHtmlEditorWidget):

    def render(self, name, value, attrs=None):
        import re
        match = re.search(r'_([a-z][a-z])$', name)
        if match is None:
            lang = 'en'
        else:
            lang = match.group(1)
        default_attrs = {'class': '%s lang_%s' %(self.attrs.get('class',''),lang)}
        if attrs:
            default_attrs.update(attrs)
        return super(Htmli18nEditor, self).render(name, value, default_attrs)
