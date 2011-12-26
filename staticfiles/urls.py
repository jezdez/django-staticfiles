import re
from django.conf.urls.defaults import patterns, url
from django.core.exceptions import ImproperlyConfigured

from staticfiles.conf import settings

urlpatterns = []


def static(prefix, view='django.views.static.serve', **kwargs):
    """
    Helper function to return a URL pattern for serving files in debug mode.

    from django.conf import settings
    from django.conf.urls.static import static

    urlpatterns = patterns('',
        # ... the rest of your URLconf goes here ...
    ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    """
    # No-op if not in debug mode or an non-local prefix
    if not settings.DEBUG or (prefix and '://' in prefix):
        return []
    elif not prefix:
        raise ImproperlyConfigured("Empty static prefix not permitted")
    return patterns('',
        url(r'^%s(?P<path>.*)$' % re.escape(prefix.lstrip('/')),
            view, kwargs=kwargs),
    )


def staticfiles_urlpatterns(prefix=None):
    """
    Helper function to return a URL pattern for serving static files.
    """
    if prefix is None:
        prefix = settings.STATIC_URL
    return static(prefix, view='staticfiles.views.serve')

# Only append if urlpatterns are empty
if settings.DEBUG and not urlpatterns:
    urlpatterns += staticfiles_urlpatterns()
