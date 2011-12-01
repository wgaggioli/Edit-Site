from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('editsite.views',
    url(r'^$', 'home', name='editsite-home'),
    url(r'^(?P<uri>[\w\-]+)$', 'page', name="editsite-page")
)
