from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

# The directory in which the static files are collected in
ROOT = getattr(settings, 'STATIC_ROOT', '')

# The URL path to STATIC_ROOT
URL = getattr(settings, 'STATIC_URL', None)

# A tuple of two-tuples with a name and the path of additional directories
# which hold static files and should be taken into account
DIRS = getattr(settings, 'STATICFILES_DIRS', ())

# Apps that have media in <app>/media, not in <app>/media/<app>,
# e.g. django.contrib.admin
PREPEND_LABEL_APPS = getattr(settings, 'STATICFILES_PREPEND_LABEL_APPS',
                             ('django.contrib.admin',))

# Apps that shouldn't be taken into account when collecting app media
EXCLUDED_APPS = getattr(settings, 'STATICFILES_EXCLUDED_APPS', ())

# Destination storage
STORAGE = getattr(settings, 'STATICFILES_STORAGE',
                  'staticfiles.storage.StaticFilesStorage')

# List of resolver classes that know how to find static files in
# various locations.
if getattr(settings, 'STATICFILES_RESOLVERS', None):
    raise ImproperlyConfigured(
        "The resolver API has been replaced by the finders API and "
        "its STATICFILES_FINDERS setting. Please update your settings.")

# List of finder classes that know how to find static files in
# various locations.
FINDERS = getattr(settings, 'STATICFILES_FINDERS',
                  ('staticfiles.finders.FileSystemFinder',
                   'staticfiles.finders.AppDirectoriesFinder',
#                  'staticfiles.finders.DefaultStorageFinder'
                  ))
