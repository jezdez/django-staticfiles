from django.conf.urls.defaults import *  # noqa

urlpatterns = patterns('',
    url(r'^static/(?P<path>.*)$', 'staticfiles.views.serve'),
)
