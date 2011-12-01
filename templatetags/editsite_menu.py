from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def superfish_menu(menu, autoescape=None, top=True):
    html = u'<ul class="superfish_menu%s">' %(u' supernav' if top else u'')
    esc = conditional_escape if autoescape else lambda x: x
    for page in menu:
        html += u'<li'
        if page['active']:
            html += u' class="active"'
        html += u'>'
        if page['clickable']:
            html += u'<a href="%s">%s</a>' %(page['url'], esc(page['title']))
        else:
            html += u'<span>%s</span>' %esc(page['title'])
        if page['children']:
            html += superfish_menu(page['children'], autoescape, False)
        html += u'</li>'
    html += u'</ul>'
    if top:
        html += u'<div class="clear"></div>'
    return mark_safe(html)

superfish_menu.needs_autoescape = True
