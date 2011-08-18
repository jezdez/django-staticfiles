import os
import sys

SITE_ID = 1

TEST_ROOT = os.path.dirname(os.path.abspath(__file__))

DATABASE_ENGINE = 'sqlite3'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

MEDIA_URL = '/media/'

MEDIA_ROOT = os.path.join(TEST_ROOT, 'project', 'site_media', 'media')

ADMIN_MEDIA_PREFIX = '/static/admin/'

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(TEST_ROOT, 'project', 'site_media', 'static')

STATICFILES_STORAGE = 'staticfiles.storage.StaticFilesStorage'

STATICFILES_DIRS = (
    os.path.join(TEST_ROOT, 'project', 'documents'),
    ('prefix', os.path.join(TEST_ROOT, 'project', 'prefixed')),
)

STATICFILES_EXCLUDED_APPS = (
    'tests.apps.skip',
)

STATICFILES_FINDERS = (
    'staticfiles.finders.FileSystemFinder',
    'staticfiles.finders.AppDirectoriesFinder',
    'staticfiles.finders.DefaultStorageFinder',
)

ROOT_URLCONF = 'tests.urls'

TEMPLATE_DIRS = (
    os.path.join(TEST_ROOT, 'project', 'templates'),
)

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.admin',
    'staticfiles',
    'tests',
    'tests.apps.test',
    'tests.apps.no_label',
    'tests.apps.skip',
]

