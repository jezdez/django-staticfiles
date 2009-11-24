from tempfile import mkdtemp
import shutil
import os
import sys
from cStringIO import StringIO
import posixpath

from django.test import TestCase, Client
from django.conf import settings as django_settings
from django.core.management import call_command

from staticfiles import settings

class BaseFileResolutionTests:
    """
    Tests shared by all file-resolving features (build_static,
    resolve_static, and static serve view).

    """
    def assertFileContains(self, filepath, text):
        self.failUnless(text in self._get_file(filepath),
                        "'%s' not in '%s'" % (text, filepath))

    def assertFileNotFound(self, filepath):
        self.assertRaises(IOError, self._get_file, filepath)
        
    def test_staticfiles_dirs(self):
        """
        Can find a file in a STATICFILES_DIRS directory.
        
        """
        self.assertFileContains('test.txt', 'Can we find')
            
    def test_staticfiles_dirs_subdir(self):
        """
        Can find a file in a subdirectory of a STATICFILES_DIRS
        directory.

        """
        self.assertFileContains('subdir/test.txt', 'Can we find')
            
    def test_staticfiles_dirs_priority(self):
        """
        File in STATICFILES_DIRS has priority over file in app.

        """
        self.assertFileContains('test/file.txt', 'STATICFILES_DIRS')

    def test_app_files(self):
        """
        Can find a file in an app media/ directory.
        
        """
        self.assertFileContains('test/file1.txt', 'file1 in the app dir')

    def test_prepend_label_apps(self):
        """
        Can find a file in an app media/ directory using
        STATICFILES_PREPEND_LABEL_APPS.
        
        """
        self.assertFileContains('no_label/file2.txt', 'file2 in no_label')

    def test_excluded_apps(self):
        """
        Can not find file in an app in STATICFILES_EXCLUDED_APPS.
        
        """
        self.assertFileNotFound('skip/skip_file.txt')

class TestResolveStatic(TestCase, BaseFileResolutionTests):
    """
    Test ``resolve_static`` management command.

    TODO: test without --first, test STATICFILES_MEDIA_DIRNAMES

    """
    def _get_file(self, filepath):
        _stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            call_command('resolve_static', filepath, all=False, verbosity='0')
            sys.stdout.seek(0)
            contents = open(sys.stdout.read().strip()).read()
        finally:
            sys.stdout = _stdout
        return contents

        
class TestBuildStatic(TestCase, BaseFileResolutionTests):
    """
    Test ``build_static`` management command.

    TODO: test -i, -n, -l, --exclude-dirs, --no-default-ignore
          test alternate storages

    """
    def setUp(self):
        self._old_root = settings.ROOT
        self.root = settings.ROOT = mkdtemp()
        call_command('build_static', interactive=False, verbosity='0')

    def tearDown(self):
        shutil.rmtree(self.root)
        settings.ROOT = self._old_root

    def _get_file(self, filepath):
        return open(os.path.join(self.root, filepath)).read()

    
class TestServeStatic(TestCase, BaseFileResolutionTests):
    """
    Test static asset serving view.

    """
    def setUp(self):
        self.client = Client()

    def _response(self, url):
        return self.client.get(posixpath.join(settings.URL, url))
    
    def assertFileContains(self, filepath, text):
        self.assertContains(self._response(filepath), text)

    def assertFileNotFound(self, filepath):
        self.assertEquals(self._response(filepath).status_code, 404)

        
class TestServeMedia(TestCase):
    """
    Test serving media from MEDIA_URL.

    """
    def test_serve_media(self):
        client = Client()
        response = client.get(posixpath.join(django_settings.MEDIA_URL,
                                             'media-file.txt'))
        self.assertContains(response, 'Media file.')
