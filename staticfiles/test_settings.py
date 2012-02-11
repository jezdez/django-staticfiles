import os

SITE_ID = 1

TEST_ROOT = os.path.join(os.path.normcase(os.path.dirname(os.path.abspath(__file__))), 'tests')

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

STATICFILES_IGNORE_PATTERNS = (
    '*.ignoreme4',
    os.path.join('test', '*.ignoreme5'),
    os.path.join(TEST_ROOT, 'project', 'documents', 'test', '*.ignoreme6'),
    os.path.join('prefix', '*.ignoreme7'),
    os.path.join(TEST_ROOT, 'project', 'documents', 'ignored'),
)

STATICFILES_EXCLUDED_APPS = (
    'staticfiles.tests.apps.skip',
)

STATICFILES_FINDERS = (
    'staticfiles.finders.FileSystemFinder',
    'staticfiles.finders.AppDirectoriesFinder',
    'staticfiles.finders.DefaultStorageFinder',
)

ROOT_URLCONF = 'staticfiles.tests.urls.default'

TEMPLATE_DIRS = (
    os.path.join(TEST_ROOT, 'project', 'templates'),
)

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.auth',
    'django.contrib.admin',
    'staticfiles',
    'staticfiles.tests',
    'staticfiles.tests.apps.test',
    'staticfiles.tests.apps.no_label',
    'staticfiles.tests.apps.skip',
    'django_jenkins',
]

JENKINS_TASKS = (
    'django_jenkins.tasks.run_pyflakes',
    'django_jenkins.tasks.run_pep8',
    'django_jenkins.tasks.with_coverage',
    'django_jenkins.tasks.django_tests',
)
