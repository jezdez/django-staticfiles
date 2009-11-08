import re
from django.conf.urls.defaults import patterns, url
from django.conf import settings

from staticfiles.settings import URL as STATIC_URL

urlpatterns = []

if ':' not in STATIC_URL:
    base_url = re.escape(STATIC_URL[1:])
    urlpatterns += patterns('staticfiles.views',
        url(r'^%s(?P<path>.*)$' % base_url, 'serve'),
    )

if settings.MEDIA_ROOT and settings.MEDIA_URL and \
                        ':' not in settings.MEDIA_URL:
    base_url = re.escape(settings.MEDIA_URL[1:])
    urlpatterns += patterns('django.views.static',
        url(r'^%s(?P<path>.*)$' % base_url, 'serve',
            {'document_root': settings.MEDIA_ROOT}),
    )
