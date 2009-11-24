from os.path import dirname, join
TEST_ROOT = dirname(__file__)

INSTALLED_APPS = ('staticfiles', 'tests',
                  'tests.apps.test',
                  'tests.apps.skip',
                  'tests.apps.no_label')

DATABASE_ENGINE = 'sqlite3'

SITE_ID = 1

MEDIA_URL = '/site_media/media/'
MEDIA_ROOT = join(TEST_ROOT, 'project', 'site_media', 'media')

STATIC_URL = '/site_media/static/'
STATIC_ROOT = join(TEST_ROOT, 'project', 'site_media', 'static')

STATICFILES_DIRS = (('', join(TEST_ROOT, 'project', 'static')),)
STATICFILES_PREPEND_LABEL_APPS = ('tests.apps.no_label',)
STATICFILES_EXCLUDED_APPS = ('tests.apps.skip',)
STATICFILES_MEDIA_DIRNAMES = ('media', 'otherdir')

ROOT_URLCONF = 'tests.urls'

TEMPLATE_DIRS = (join(TEST_ROOT, 'project', 'templates'),)
