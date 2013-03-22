from django.conf.urls import *  # noqa

urlpatterns = patterns('',
    url(r'^static/(?P<path>.*)$', 'staticfiles.views.serve'),
)
