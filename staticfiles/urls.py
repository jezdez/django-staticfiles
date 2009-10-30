import re
from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = []

if ':' not in settings.STATIC_URL:
    base_url = re.escape(settings.STATIC_URL[1:])
    urlpatterns += patterns('staticfiles.views',
        url(r'^%s(?P<path>.*)$' % base_url, 'serve'),
    )

if ':' not in settings.MEDIA_URL:
    base_url = re.escape(settings.MEDIA_URL[1:])
    urlpatterns += patterns('django.views.static',
        url(r'^%s(?P<path>.*)$' % base_url, 'serve',
            {'document_root': settings.MEDIA_ROOT}),
    )
