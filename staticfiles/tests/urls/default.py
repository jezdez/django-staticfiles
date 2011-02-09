from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^static/(?P<path>.*)$', 'staticfiles.views.serve'),
)
