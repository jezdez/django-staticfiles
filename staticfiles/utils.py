import os
import fnmatch
import warnings

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from django.core.files.storage import FileSystemStorage
from django.utils.importlib import import_module

from staticfiles.settings import (URL as STATIC_URL, ROOT as STATIC_ROOT,
    MEDIA_DIRNAMES, PREPEND_LABEL_APPS, EXCLUDED_APPS)

def get_files_for_app(app, ignore_patterns=[]):
    """
    Return a list containing the relative source paths for all files that
    should be copied for an app.
    
    """
    from staticfiles.storage import AppStaticStorage
    warnings.warn(
        "The staticfiles.utils.get_files_for_app utility function is "
        "deprecated. Use staticfiles.storage.AppStaticStorage.get_files "
        "instead.", PendingDeprecationWarning)
    return AppStaticStorage(app).get_files(ignore_patterns)

def get_app_prefix(app):
    """
    Return the path name that should be prepended to files for this app.
    """
    from staticfiles.storage import AppStaticStorage
    warnings.warn(
        "The staticfiles.utils.get_app_prefix utility function is "
        "deprecated. Use staticfiles.storage.AppStaticStorage.get_prefix "
        "instead.", PendingDeprecationWarning)
    return AppStaticStorage(app).get_prefix()

def get_files(storage, ignore_patterns=[], location=''):
    """
    Recursively walk the storage directories gathering a complete list of files
    that should be copied, returning this list.
    
    """
    def is_ignored(path):
        """
        Return True or False depending on whether the ``path`` should be
        ignored (if it matches any pattern in ``ignore_patterns``).
        
        """
        for pattern in ignore_patterns:
            if fnmatch.fnmatchcase(path, pattern):
                return True
        return False

    directories, files = storage.listdir(location)
    static_files = [location and os.path.join(location, fn) or fn
                    for fn in files
                    if not is_ignored(fn)]
    for dir in directories:
        if is_ignored(dir):
            continue
        if location:
            dir = os.path.join(location, dir)
        static_files.extend(get_files(storage, ignore_patterns, dir))
    return static_files

def check_settings():
    """
    Checks if the MEDIA_(ROOT|URL) and STATIC_(ROOT|URL)
    settings have the same value.
    """
    if settings.MEDIA_URL == STATIC_URL:
        raise ImproperlyConfigured("The MEDIA_URL and STATIC_URL "
                                   "settings must have different values")
    if ((settings.MEDIA_ROOT and STATIC_ROOT) and
            (settings.MEDIA_ROOT == STATIC_ROOT)):
        raise ImproperlyConfigured("The MEDIA_ROOT and STATIC_ROOT "
                                   "settings must have different values")
