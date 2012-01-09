# -*- encoding: utf-8 -*-
from __future__ import with_statement
import codecs
import os
import stat
import posixpath
import shutil
import sys
import tempfile
import unittest2
from StringIO import StringIO

from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import default_storage
from django.core.management import call_command
from django.template import loader, Context
from django.test import TestCase
from django.utils.encoding import smart_unicode

try:
    from django.utils.functional import empty
except ImportError:
    empty = None

from staticfiles import finders, storage
from staticfiles.conf import settings


def rmtree_errorhandler(func, path, exc_info):
    """
    On Windows, some files are read-only (e.g. in in .svn dirs), so when
    rmtree() tries to remove them, an exception is thrown.
    We catch that here, remove the read-only attribute, and hopefully
    continue without problems.
    """
    exctype, value = exc_info[:2]
    # lookin for a windows error
    if exctype is not WindowsError or 'Access is denied' not in str(value):
        raise
    # file type should currently be read only
    if ((os.stat(path).st_mode & stat.S_IREAD) != stat.S_IREAD):
        raise
    # convert to read/write
    os.chmod(path, stat.S_IWRITE)
    # use the original function to repeat the operation
    func(path)


class BaseStaticFilesTestCase(object):
    """
    Test case with a couple utility assertions.
    """
    def setUp(self):
        # Clear the cached default_storage out, this is because when it first
        # gets accessed (by some other test), it evaluates settings.MEDIA_ROOT,
        # since we're planning on changing that we need to clear out the cache.
        default_storage._wrapped = empty
        storage.staticfiles_storage._wrapped = empty

        self.old_debug = settings.DEBUG
        settings.DEBUG = True

        testfiles_path = os.path.join(settings.TEST_ROOT, 'apps', 'test', 'static', 'test')
        # To make sure SVN doesn't hangs itself with the non-ASCII characters
        # during checkout, we actually create one file dynamically.
        self._nonascii_filepath = os.path.join(testfiles_path, u'fi\u015fier.txt')
        with codecs.open(self._nonascii_filepath, 'w', 'utf-8') as f:
            f.write(u"fi\u015fier in the app dir")
        # And also create the stupid hidden file to dwarf the setup.py's
        # package data handling.
        self._hidden_filepath = os.path.join(testfiles_path, '.hidden')
        with codecs.open(self._hidden_filepath, 'w', 'utf-8') as f:
            f.write("should be ignored")
        self._backup_filepath = os.path.join(
            settings.TEST_ROOT, 'project', 'documents', 'test', 'backup~')
        with codecs.open(self._backup_filepath, 'w', 'utf-8') as f:
            f.write("should be ignored")

    def tearDown(self):
        os.unlink(self._nonascii_filepath)
        os.unlink(self._hidden_filepath)
        os.unlink(self._backup_filepath)
        settings.DEBUG = self.old_debug

    def assertFileContains(self, filepath, text):
        self.assertIn(text, self._get_file(smart_unicode(filepath)),
                        u"'%s' not in '%s'" % (text, filepath))

    def assertFileNotFound(self, filepath):
        self.assertRaises(IOError, self._get_file, filepath)

    def render_template(self, template, **kwargs):
        if isinstance(template, basestring):
            template = loader.get_template_from_string(template)
        return template.render(Context(kwargs)).strip()

    def static_template_snippet(self, path):
        return "{%% load staticfiles %%}{%% static '%s' %%}" % path

    def assertStaticRenders(self, path, result, **kwargs):
        template = self.static_template_snippet(path)
        self.assertEqual(self.render_template(template, **kwargs), result)

    def assertStaticRaises(self, exc, path, result, **kwargs):
        self.assertRaises(exc, self.assertStaticRenders, path, result, **kwargs)


class StaticFilesTestCase(BaseStaticFilesTestCase, TestCase, unittest2.TestCase):
    pass


class BaseCollectionTestCase(BaseStaticFilesTestCase, unittest2.TestCase):
    """
    Tests shared by all file finding features (collectstatic,
    findstatic, and static serve view).

    This relies on the asserts defined in BaseStaticFilesTestCase, but
    is separated because some test cases need those asserts without
    all these tests.
    """
    def setUp(self):
        super(BaseCollectionTestCase, self).setUp()
        self.old_root = settings.STATIC_ROOT
        settings.STATIC_ROOT = tempfile.mkdtemp(prefix='staticfiles_')
        self.run_collectstatic()

    def tearDown(self):
        # Use our own error handler that can handle .svn dirs on Windows
        shutil.rmtree(settings.STATIC_ROOT, ignore_errors=True, onerror=rmtree_errorhandler)
        settings.STATIC_ROOT = self.old_root
        super(BaseCollectionTestCase, self).tearDown()

    def run_collectstatic(self, **kwargs):
        ignore_patterns = [
            '*.ignoreme', os.path.join('test', '*.ignoreme2'), os.path.join(
                TEST_ROOT, 'apps', 'test', 'static', 'test', '*.ignoreme3')]
        call_command('collectstatic', interactive=False, verbosity='0',
                     ignore_patterns=ignore_patterns, **kwargs)

    def _get_file(self, filepath):
        assert filepath, 'filepath is empty.'
        filepath = os.path.join(settings.STATIC_ROOT, filepath)
        with codecs.open(filepath, "r", "utf-8") as f:
            return f.read()


class CollectionTestCase(BaseCollectionTestCase, StaticFilesTestCase):
    pass


class TestDefaults(object):
    """
    A few standard test cases.
    """
    def test_staticfiles_dirs(self):
        """
        Can find a file in a STATICFILES_DIRS directory.
        """
        self.assertFileContains('test.txt', 'Can we find')
        self.assertFileContains(os.path.join('prefix', 'test.txt'), 'Prefix')

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
        Can find a file in an app static/ directory.
        """
        self.assertFileContains('test/file1.txt', 'file1 in the app dir')

    def test_nonascii_filenames(self):
        """
        Can find a file with non-ASCII character in an app static/ directory.
        """
        self.assertFileContains(u'test/fişier.txt', u'fişier in the app dir')

    def test_camelcase_filenames(self):
        """
        Can find a file with capital letters.
        """
        self.assertFileContains(u'test/camelCase.txt', u'camelCase')

    def test_excluded_apps(self):
        """
        Can not find file in an app in STATICFILES_EXCLUDED_APPS.
        """
        self.assertFileNotFound('skip/skip_file.txt')


class TestFindStatic(CollectionTestCase, TestDefaults):
    """
    Test ``findstatic`` management command.
    """
    def _get_file(self, filepath):
        _stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            call_command('findstatic', filepath, all=False, verbosity='0')
            sys.stdout.seek(0)
            lines = [l.strip() for l in sys.stdout.readlines()]
            with codecs.open(smart_unicode(lines[1].strip()), "r", "utf-8") as f:
                contents = f.read()
        except IndexError, e:
            raise IOError(e)
        finally:
            sys.stdout = _stdout
        return contents

    def test_all_files(self):
        """
        Test that findstatic returns all candidate files if run without --first.
        """
        _stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            call_command('findstatic', 'test/file.txt', verbosity='0')
            sys.stdout.seek(0)
            lines = [l.strip() for l in sys.stdout.readlines()]
        finally:
            sys.stdout = _stdout
        self.assertEqual(len(lines), 3)  # three because there is also the "Found <file> here" line
        self.assertTrue('project' in lines[1])
        self.assertTrue('apps' in lines[2])


class TestCollection(CollectionTestCase, TestDefaults):
    """
    Test ``collectstatic`` management command.
    """
    def test_ignore(self):
        """
        Test that -i patterns are ignored.
        """
        self.assertFileNotFound('test/test.ignoreme')
        self.assertFileNotFound('test/test_relative.ignoreme2')
        self.assertFileNotFound('test/test_absolute.ignoreme3')

    def test_common_ignore_patterns(self):
        """
        Common ignore patterns (*~, .*, CVS) are ignored.
        """
        self.assertFileNotFound('test/.hidden')
        self.assertFileNotFound('test/backup~')
        self.assertFileNotFound('test/CVS')

    def test_staticfiles_ignore_patterns(self):
        """
        Test that patterns in STATICFILES_IGNORE_PATTERNS are ignored.
        """
        self.assertFileNotFound('test/test.ignoreme4')
        self.assertFileNotFound('test/test_relative.ignoreme5')
        self.assertFileNotFound('test/test_absolute.ignoreme6')
        self.assertFileNotFound('prefix/test.ignoreme7')
        self.assertFileNotFound('ignored/test_directory.txt')


class TestCollectionClear(CollectionTestCase):
    """
    Test the ``--clear`` option of the ``collectstatic`` managemenet command.
    """
    def run_collectstatic(self, **kwargs):
        clear_filepath = os.path.join(settings.STATIC_ROOT, 'cleared.txt')
        with open(clear_filepath, 'w') as f:
            f.write('should be cleared')
        super(TestCollectionClear, self).run_collectstatic(clear=True)

    def test_cleared_not_found(self):
        self.assertFileNotFound('cleared.txt')


class TestCollectionExcludeNoDefaultIgnore(CollectionTestCase, TestDefaults):
    """
    Test ``--exclude-dirs`` and ``--no-default-ignore`` options of the
    ``collectstatic`` management command.
    """
    def run_collectstatic(self):
        super(TestCollectionExcludeNoDefaultIgnore, self).run_collectstatic(
            use_default_ignore_patterns=False)

    def test_no_common_ignore_patterns(self):
        """
        With --no-default-ignore, common ignore patterns (*~, .*, CVS)
        are not ignored.

        """
        self.assertFileContains('test/.hidden', 'should be ignored')
        self.assertFileContains('test/backup~', 'should be ignored')
        self.assertFileContains('test/CVS', 'should be ignored')


class TestNoFilesCreated(object):

    def test_no_files_created(self):
        """
        Make sure no files were create in the destination directory.
        """
        self.assertEqual(os.listdir(settings.STATIC_ROOT), [])


class TestCollectionDryRun(CollectionTestCase, TestNoFilesCreated):
    """
    Test ``--dry-run`` option for ``collectstatic`` management command.
    """
    def run_collectstatic(self):
        super(TestCollectionDryRun, self).run_collectstatic(dry_run=True)


class TestCollectionNonLocalStorage(CollectionTestCase, TestNoFilesCreated):
    """
    Tests for #15035
    """
    def setUp(self):
        self.old_staticfiles_storage = settings.STATICFILES_STORAGE
        settings.STATICFILES_STORAGE = 'staticfiles.tests.storage.DummyStorage'
        super(TestCollectionNonLocalStorage, self).setUp()

    def tearDown(self):
        super(TestCollectionNonLocalStorage, self).tearDown()
        settings.STATICFILES_STORAGE = self.old_staticfiles_storage


class TestCollectionCachedStorage(BaseCollectionTestCase, BaseStaticFilesTestCase, TestCase):
    """
    Tests for the Cache busting storage
    """
    def setUp(self):
        # we set DEBUG to False here since the template tag wouldn't work otherwise
        self.old_staticfiles_storage = settings.STATICFILES_STORAGE
        settings.STATICFILES_STORAGE = 'staticfiles.storage.CachedStaticFilesStorage'
        super(TestCollectionCachedStorage, self).setUp()
        self.old_debug = settings.DEBUG
        settings.DEBUG = False

    def tearDown(self):
        super(TestCollectionCachedStorage, self).tearDown()
        settings.STATICFILES_STORAGE = self.old_staticfiles_storage
        settings.DEBUG = self.old_debug

    def cached_file_path(self, relpath):
        template = "{%% load staticfiles %%}{%% static '%s' %%}"
        fullpath = self.render_template(template % relpath)
        return fullpath.replace(settings.STATIC_URL, '')

    def test_template_tag_return(self):
        """
        Test the CachedStaticFilesStorage backend.
        """
        self.assertStaticRaises(ValueError,
                                "does/not/exist.png",
                                "/static/does/not/exist.png")
        self.assertStaticRenders("test/file.txt",
                                 "/static/test/file.dad0999e4f8f.txt")
        self.assertStaticRenders("cached/styles.css",
                                 "/static/cached/styles.93b1147e8552.css")

    def test_template_tag_simple_content(self):
        relpath = self.cached_file_path("cached/styles.css")
        self.assertEqual(relpath, "cached/styles.93b1147e8552.css")
        with storage.staticfiles_storage.open(relpath) as relfile:
            content = relfile.read()
            self.assertNotIn("cached/other.css", content)
            self.assertIn("/static/cached/other.d41d8cd98f00.css", content)

    def test_path_with_querystring(self):
        relpath = self.cached_file_path("cached/styles.css?spam=eggs")
        self.assertEqual(relpath,
                         "cached/styles.93b1147e8552.css?spam=eggs")
        with storage.staticfiles_storage.open(
                "cached/styles.93b1147e8552.css") as relfile:
            content = relfile.read()
            self.assertNotIn("cached/other.css", content)
            self.assertIn("/static/cached/other.d41d8cd98f00.css", content)

    def test_path_with_fragment(self):
        relpath = self.cached_file_path("cached/styles.css#eggs")
        self.assertEqual(relpath, "cached/styles.93b1147e8552.css#eggs")
        with storage.staticfiles_storage.open(
                "cached/styles.93b1147e8552.css") as relfile:
            content = relfile.read()
            self.assertNotIn("cached/other.css", content)
            self.assertIn("/static/cached/other.d41d8cd98f00.css", content)

    def test_path_with_querystring_and_fragment(self):
        relpath = self.cached_file_path("cached/css/fragments.css")
        self.assertEqual(relpath, "cached/css/fragments.75433540b096.css")
        with storage.staticfiles_storage.open(relpath) as relfile:
            content = relfile.read()
            self.assertIn('/static/cached/css/fonts/font.a4b0478549d0.eot?#iefix', content)
            self.assertIn('/static/cached/css/fonts/font.b8d603e42714.svg#webfontIyfZbseF', content)
            self.assertIn('data:font/woff;charset=utf-8;base64,d09GRgABAAAAADJoAA0AAAAAR2QAAQAAAAAAAAAAAAA', content)
            self.assertIn('#default#VML', content)

    def test_template_tag_absolute(self):
        relpath = self.cached_file_path("cached/absolute.css")
        self.assertEqual(relpath, "cached/absolute.cc80cb5e2eb1.css")
        with storage.staticfiles_storage.open(relpath) as relfile:
            content = relfile.read()
            self.assertNotIn("/static/cached/styles.css", content)
            self.assertIn("/static/cached/styles.93b1147e8552.css", content)

    def test_template_tag_denorm(self):
        relpath = self.cached_file_path("cached/denorm.css")
        self.assertEqual(relpath, "cached/denorm.363de96e9b4b.css")
        with storage.staticfiles_storage.open(relpath) as relfile:
            content = relfile.read()
            self.assertNotIn("..//cached///styles.css", content)
            self.assertIn("/static/cached/styles.93b1147e8552.css", content)

    def test_template_tag_relative(self):
        relpath = self.cached_file_path("cached/relative.css")
        self.assertEqual(relpath, "cached/relative.8dffb45d91f5.css")
        with storage.staticfiles_storage.open(relpath) as relfile:
            content = relfile.read()
            self.assertIn("/static/cached/styles.93b1147e8552.css", content)
            self.assertNotIn("../cached/styles.css", content)
            self.assertNotIn('@import "styles.css"', content)
            self.assertNotIn('url(img/relative.png)', content)
            self.assertIn('url("/static/cached/img/relative.acae32e4532b.png")', content)
            self.assertIn("/static/cached/styles.93b1147e8552.css", content)

    def test_template_tag_deep_relative(self):
        relpath = self.cached_file_path("cached/css/window.css")
        self.assertEqual(relpath, "cached/css/window.9db38d5169f3.css")
        with storage.staticfiles_storage.open(relpath) as relfile:
            content = relfile.read()
            self.assertNotIn('url(img/window.png)', content)
            self.assertIn('url("/static/cached/css/img/window.acae32e4532b.png")', content)

    def test_template_tag_url(self):
        relpath = self.cached_file_path("cached/url.css")
        self.assertEqual(relpath, "cached/url.615e21601e4b.css")
        with storage.staticfiles_storage.open(relpath) as relfile:
            self.assertIn("https://", relfile.read())


if sys.platform != 'win32':

    class TestCollectionLinks(CollectionTestCase, TestDefaults):
        """
        Test ``--link`` option for ``collectstatic`` management command.

        Note that by inheriting ``TestDefaults`` we repeat all
        the standard file resolving tests here, to make sure using
        ``--link`` does not change the file-selection semantics.
        """
        def run_collectstatic(self):
            super(TestCollectionLinks, self).run_collectstatic(link=True)

        def test_links_created(self):
            """
            With ``--link``, symbolic links are created.
            """
            self.assertTrue(os.path.islink(os.path.join(settings.STATIC_ROOT, 'test.txt')))


class TestServeStatic(StaticFilesTestCase):
    """
    Test static asset serving view.
    """
    urls = 'staticfiles.tests.urls.default'

    def _response(self, filepath):
        return self.client.get(
            posixpath.join(settings.STATIC_URL, filepath))

    def assertFileContains(self, filepath, text):
        self.assertContains(self._response(filepath), text)

    def assertFileNotFound(self, filepath):
        self.assertEquals(self._response(filepath).status_code, 404)


class TestServeDisabled(TestServeStatic):
    """
    Test serving static files disabled when DEBUG is False.
    """
    def setUp(self):
        super(TestServeDisabled, self).setUp()
        self.old_debug = settings.DEBUG
        settings.DEBUG = False

    def tearDown(self):
        super(TestServeDisabled, self).tearDown()
        settings.DEBUG = self.old_debug

    def test_disabled_serving(self):
        self.assertRaises(ImproperlyConfigured, self._response, 'test.txt')


class TestServeStaticWithDefaultURL(TestServeStatic, TestDefaults):
    """
    Test static asset serving view with manually configured URLconf.
    """
    pass


class TestServeStaticWithURLHelper(TestServeStatic, TestDefaults):
    """
    Test static asset serving view with staticfiles_urlpatterns helper.
    """
    urls = 'staticfiles.tests.urls.helper'


class TestServeAdminMedia(TestServeStatic):
    """
    Test serving media from django.contrib.admin.
    """
    def _response(self, filepath):
        return self.client.get(
            posixpath.join(settings.STATIC_URL, 'admin/', filepath))

    def test_serve_admin_media(self):
        self.assertFileContains('css/base.css', 'body')


class FinderTestCase(object):
    """
    Base finder test mixin.

    On Windows, sometimes the case of the path we ask the finders for and the
    path(s) they find can differ. Compare them using os.path.normcase() to
    avoid false negatives.
    """
    def test_find_first(self):
        src, dst = self.find_first
        found = self.finder.find(src)
        self.assertEqual(os.path.normcase(found), os.path.normcase(dst))

    def test_find_all(self):
        src, dst = self.find_all
        found = self.finder.find(src, all=True)
        found = [os.path.normcase(f) for f in found]
        dst = [os.path.normcase(d) for d in dst]
        self.assertEqual(found, dst)


class TestFileSystemFinder(StaticFilesTestCase, FinderTestCase):
    """
    Test FileSystemFinder.
    """
    def setUp(self):
        super(TestFileSystemFinder, self).setUp()
        self.finder = finders.FileSystemFinder()
        test_file_path = os.path.join(settings.TEST_ROOT, 'project', 'documents', 'test', 'file.txt')
        self.find_first = (os.path.join('test', 'file.txt'), test_file_path)
        self.find_all = (os.path.join('test', 'file.txt'), [test_file_path])


class TestAppDirectoriesFinder(StaticFilesTestCase, FinderTestCase):
    """
    Test AppDirectoriesFinder.
    """
    def setUp(self):
        super(TestAppDirectoriesFinder, self).setUp()
        self.finder = finders.AppDirectoriesFinder()
        test_file_path = os.path.join(settings.TEST_ROOT, 'apps', 'test', 'static', 'test', 'file1.txt')
        self.find_first = (os.path.join('test', 'file1.txt'), test_file_path)
        self.find_all = (os.path.join('test', 'file1.txt'), [test_file_path])


class TestDefaultStorageFinder(StaticFilesTestCase, FinderTestCase):
    """
    Test DefaultStorageFinder.
    """
    def setUp(self):
        super(TestDefaultStorageFinder, self).setUp()
        self.finder = finders.DefaultStorageFinder(
            storage=storage.StaticFilesStorage(location=settings.MEDIA_ROOT))
        test_file_path = os.path.join(settings.MEDIA_ROOT, 'media-file.txt')
        self.find_first = ('media-file.txt', test_file_path)
        self.find_all = ('media-file.txt', [test_file_path])


class TestMiscFinder(TestCase):
    """
    A few misc finder tests.
    """
    def test_get_finder(self):
        self.assertTrue(isinstance(finders.get_finder(
            'staticfiles.finders.FileSystemFinder'),
            finders.FileSystemFinder))

    def test_get_finder_bad_classname(self):
        self.assertRaises(ImproperlyConfigured, finders.get_finder,
                          'staticfiles.finders.FooBarFinder')

    def test_get_finder_bad_module(self):
        self.assertRaises(ImproperlyConfigured,
            finders.get_finder, 'foo.bar.FooBarFinder')

    def test_non_tuple_raises_exception(self):
        """
        We can't determine if STATICFILES_DIRS is set correctly just by
        looking at the type, but we can determine if it's definitely wrong.
        """
        try:
            old_staticfiles_dirs = settings.STATICFILES_DIRS
            settings.STATICFILES_DIRS = 'a string'
            self.assertRaises(ImproperlyConfigured, finders.FileSystemFinder)
        finally:
            settings.STATICFILES_DIRS = old_staticfiles_dirs


class TestTemplateTag(StaticFilesTestCase):

    def test_template_tag(self):
        self.assertStaticRenders("does/not/exist.png",
                                   "/static/does/not/exist.png")
        self.assertStaticRenders("testfile.txt", "/static/testfile.txt")
