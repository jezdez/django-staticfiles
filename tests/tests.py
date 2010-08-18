from tempfile import mkdtemp
import shutil
import os
import sys
from cStringIO import StringIO
import posixpath

from django.test import TestCase, Client
from django.conf import settings as django_settings
from django.core.management import call_command

from staticfiles import settings, resolvers


class UtilityAssertsTestCase(TestCase):
    """
    Test case with a couple utility assertions.

    """
    def assertFileContains(self, filepath, text):
        self.failUnless(text in self._get_file(filepath),
                        "'%s' not in '%s'" % (text, filepath))

    def assertFileNotFound(self, filepath):
        self.assertRaises(IOError, self._get_file, filepath)

    def _get_file(self, filepath):
        raise NotImplementedError
        
class BaseFileResolutionTests:
    """
    Tests shared by all file-resolving features (build_static,
    resolve_static, and static serve view).
    
    This relies on the asserts defined in UtilityAssertsTestCase, but
    is separated because some test cases need those asserts without
    all these tests.

    """
    def assertFileContains(self, filepath, text):
        raise NotImplementedError
    
    def assertFileNotFound(self, filepath):
        raise NotImplementedError
        
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

    def test_staticfiles_media_dirnames(self):
        """
        Can find a file in an app subdirectory whose name is listed in
        STATICFILES_MEDIA_DIRNAMES setting.

        """
        self.assertFileContains('odfile.txt', 'File in otherdir.')

        
class TestResolveStatic(UtilityAssertsTestCase, BaseFileResolutionTests):
    """
    Test ``resolve_static`` management command.

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

    def test_all_files(self):
        """
        Test that resolve_static returns all candidate files if run
        without --first.

        """
        _stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            call_command('resolve_static', 'test/file.txt', verbosity='0')
            sys.stdout.seek(0)
            lines = [l.strip() for l in sys.stdout.readlines()]
        finally:
            sys.stdout = _stdout
        self.assertEquals(len(lines), 2)
        self.failUnless('project' in lines[0])
        self.failUnless('apps' in lines[1])

        
class BuildStaticTestCase(UtilityAssertsTestCase):
    """
    Base setup for build_static tests.

    """
    def setUp(self):
        self._old_root = settings.ROOT
        self.root = settings.ROOT = mkdtemp()
        self.run_build_static()

    def run_build_static(self, **kwargs):
        call_command('build_static', interactive=False, verbosity='0',
                     ignore_patterns=['*.ignoreme'], **kwargs)

    def tearDown(self):
        shutil.rmtree(self.root)
        settings.ROOT = self._old_root

    def _get_file(self, filepath):
        return open(os.path.join(self.root, filepath)).read()


class TestBuildStatic(BuildStaticTestCase, BaseFileResolutionTests):
    """
    Test ``build_static`` management command.

    TODO: test alternate storages

    """
    def test_ignore(self):
        """
        Test that -i patterns are ignored.

        """
        self.assertFileNotFound('test/test.ignoreme')

    def test_common_ignore_patterns(self):
        """
        Common ignore patterns (*~, .*, CVS) are ignored.

        """
        self.assertFileNotFound('test/.hidden')
        self.assertFileNotFound('test/backup~')
        self.assertFileNotFound('test/CVS')


class TestBuildStaticExcludeNoDefaultIgnore(BuildStaticTestCase):
    """
    Test ``--exclude-dirs`` and ``--no-default-ignore`` options for
    ``build_static`` management command.


    """
    def run_build_static(self):
        BuildStaticTestCase.run_build_static(self,
            exclude_dirs=True, use_default_ignore_patterns=False)

    def test_exclude_dirs(self):
        """
        With --exclude-dirs, cannot find file in
        STATICFILES_DIRS.

        """
        self.assertFileNotFound('test.txt')

    def test_no_common_ignore_patterns(self):
        """
        With --no-default-ignore, common ignore patterns (*~, .*, CVS)
        are not ignored.

        """
        self.assertFileContains('test/.hidden', 'should be ignored')
        self.assertFileContains('test/backup~', 'should be ignored')
        self.assertFileContains('test/CVS', 'should be ignored')

        
class TestBuildStaticDryRun(BuildStaticTestCase):
    """
    Test ``--dry-run`` option for ``build_static`` management command.

    """
    def run_build_static(self):
        BuildStaticTestCase.run_build_static(self, dry_run=True)

    def test_no_files_created(self):
        """
        With --dry-run, no files created in destination dir.

        """
        self.assertEquals(os.listdir(self.root), [])
    

if sys.platform != 'win32':
    class TestBuildStaticLinks(BuildStaticTestCase, BaseFileResolutionTests):
        """
        Test ``--link`` option for ``build_static`` management command.
        
        Note that by inheriting ``BaseFileResolutionTests`` we repeat all
        the standard file resolving tests here, to make sure using
        ``--link`` does not change the file-selection semantics.
        
        """
        def run_build_static(self):
            BuildStaticTestCase.run_build_static(self, link=True)

        def test_links_created(self):
            """
            With ``--link``, symbolic links are created.
            
            """
            self.failUnless(os.path.islink(os.path.join(self.root, 'test.txt')))

class TestServeStatic(UtilityAssertsTestCase, BaseFileResolutionTests):
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


class TestFileSystemResolver(UtilityAssertsTestCase):
    """
    Test FileSystemResolver.
    
    """
    def setUp(self):
        self.resolver = resolvers.FileSystemResolver()

    def test_resolve_first(self):
        result = self.resolver.resolve("test/file.txt")
        self.assertEquals(result,
            os.path.join(django_settings.TEST_ROOT, 'project', 'static', 'test/file.txt'))

    def test_resolve_all(self):
        result = self.resolver.resolve("test/file.txt", all=True)
        self.assertEquals(result,
            [os.path.join(django_settings.TEST_ROOT, 'project', 'static', 'test/file.txt')])
