import os
import fnmatch
import warnings

from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

from django.core.files.storage import FileSystemStorage
from django.utils.importlib import import_module

from staticfiles import settings

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

def is_ignored(path, ignore_patterns=[]):
    """
    Return True or False depending on whether the ``path`` should be
    ignored (if it matches any pattern in ``ignore_patterns``).
    """
    for pattern in ignore_patterns:
        if fnmatch.fnmatchcase(path, pattern):
            return True
    return False

def get_files(storage, ignore_patterns=[], location=''):
    """
    Recursively walk the storage directories yielding the paths
    of all files that should be copied.
    """
    directories, files = storage.listdir(location)
    for fn in files:
        if is_ignored(fn, ignore_patterns):
            continue
        if location:
            fn = os.path.join(location, fn)
        yield fn
    for dir in directories:
        if is_ignored(dir, ignore_patterns):
            continue
        if location:
            dir = os.path.join(location, dir)
        for fn in get_files(storage, ignore_patterns, dir):
            yield fn

def check_settings():
    """
    Checks if the staticfiles settings have sane values.
    """
    if not settings.URL:
        raise ImproperlyConfigured(
            "You're using the staticfiles app "
            "without having set the required STATIC_URL setting.")
    if django_settings.MEDIA_URL == settings.URL:
        raise ImproperlyConfigured("The MEDIA_URL and STATIC_URL "
                                   "settings must have different values")
    if ((django_settings.MEDIA_ROOT and settings.ROOT) and
            (django_settings.MEDIA_ROOT == settings.ROOT)):
        raise ImproperlyConfigured("The MEDIA_ROOT and STATIC_ROOT "
                                   "settings must have different values")
