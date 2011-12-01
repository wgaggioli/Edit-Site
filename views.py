from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings

from editsite.models import Page

def _default_page_render(page):
    params = dict(page=page)
    if page.layout.has_menu:
        params['menu'] = _assemble_menu(page)
    for field in page.xfields():
        params[field.input.varname] = field.render()
    return render_to_response('%s/%s' %(settings.LAYOUT_DIR, page.layout.template), params)

def _assemble_menu(active_page, parent=None):
    menu = []
    for page in Page.objects.filter(parent=parent, on_menu=True).order_by('menu_order'):
        menu.append({
            'url': reverse('editsite-page', kwargs=dict(uri=page.uri)),
            'title': page.title_en,
            'active': page == active_page or active_page in page.xall_children(),
            'clickable': page.accessable,
            'children': _assemble_menu(active_page, page)
        })
    return menu

def home(request):
    page = get_object_or_404(Page, uri__exact=u'home')
    return _default_page_render(page)

def page(request, uri):
    page = get_object_or_404(Page, uri__exact=uri)
    return _default_page_render(page)
