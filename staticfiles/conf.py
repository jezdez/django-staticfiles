"""
Initializes the settings
"""
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from appconf import AppConf


class StaticFilesConf(AppConf):
    # The directory in which the static files are collected in
    ROOT = ''
    # The URL path to STATIC_ROOT
    URL = None
    # A tuple of two-tuples with a name and the path of additional directories
    # which hold static files and should be taken into account
    DIRS = ()
    # Apps that shouldn't be taken into account when collecting app media
    EXCLUDED_APPS = ()
    # Destination storage
    STORAGE = 'staticfiles.storage.StaticFilesStorage'
    # List of finder classes that know how to find static files in
    # various locations.
    FINDERS = (
        'staticfiles.finders.FileSystemFinder',
        'staticfiles.finders.AppDirectoriesFinder',
    #    'staticfiles.finders.DefaultStorageFinder',
    )

    def configure_root(self, value):
        """
        Use STATIC_ROOT since it doesn't has the default prefix
        """
        root = value or getattr(settings, 'STATIC_ROOT', None)
        if (settings.MEDIA_ROOT and root) and (settings.MEDIA_ROOT == root):
            raise ImproperlyConfigured("The MEDIA_ROOT and STATIC_ROOT "
                                       "settings must have different values")
        settings.STATIC_ROOT = root
        return root

    def configure_url(self, value):
        """
        Use STATIC_URL since it doesn't has the default prefix
        """
        url = value or getattr(settings, 'STATIC_URL', None)
        if not url:
            raise ImproperlyConfigured("You're using the staticfiles app "
                                       "without having set the required "
                                       "STATIC_URL setting.")
        if url == settings.MEDIA_URL:
            raise ImproperlyConfigured("The MEDIA_URL and STATIC_URL "
                                       "settings must have different values")
        settings.STATIC_URL = url
        return url


# Okay, this is ugly, but I don't see another way except adding a registry
# pattern thingie to Django which seems like overengineering. Meh.
try:
    from django.contrib.admin.templatetags import admin_static
except ImportError:
    # We leave Django alone since there isn't a admin_static module.
    pass
else:
    # Heck, we patch the hell out of it, err, replace the default static tag.
    from staticfiles.templatetags.staticfiles import static
    admin_static.static = admin_static.register.simple_tag(static)
