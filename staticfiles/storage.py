from __future__ import with_statement
import os
import posixpath
import re
import warnings

from datetime import datetime
from urllib import unquote
from urlparse import urlsplit, urlunsplit, urldefrag

from django import VERSION
from django.conf import settings
from django.core.cache import (get_cache, InvalidCacheBackendError,
                               cache as default_cache)
from django.core.files.base import File, ContentFile
from django.core.files.storage import FileSystemStorage, get_storage_class
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import force_unicode, smart_str
from django.utils.datastructures import SortedDict
from django.utils.functional import LazyObject
from django.utils.importlib import import_module
from django.utils.hashcompat import md5_constructor

from staticfiles.utils import matches_patterns


def setattr_ifmissing(clss, name, func):
    for cls in clss:
        if not hasattr(cls, name):
            setattr(cls, name, func)


def __enter__(self):
    return self


def __exit__(self, exc_type, exc_value, tb):
    self.close()

# forcing the storage backend file to be a context manager
setattr_ifmissing([File, ContentFile], '__enter__', __enter__)
setattr_ifmissing([File, ContentFile], '__exit__', __exit__)

fragments_re = re.compile(r'([?#].*)$')


class TimeAwareFileSystemStorage(FileSystemStorage):
    def accessed_time(self, name):
        return datetime.fromtimestamp(os.path.getatime(self.path(name)))

    def created_time(self, name):
        return datetime.fromtimestamp(os.path.getctime(self.path(name)))

    def modified_time(self, name):
        return datetime.fromtimestamp(os.path.getmtime(self.path(name)))


class DefaultStorage(LazyObject):
    def _setup(self):
        self._wrapped = TimeAwareFileSystemStorage()

default_storage = DefaultStorage()


class StaticFilesStorage(TimeAwareFileSystemStorage):
    """
    Standard file system storage for static files.

    The defaults for ``location`` and ``base_url`` are
    ``STATIC_ROOT`` and ``STATIC_URL``.
    """
    def __init__(self, location=None, base_url=None, *args, **kwargs):
        if location is None:
            location = settings.STATIC_ROOT
        if base_url is None:
            base_url = settings.STATIC_URL
        super(StaticFilesStorage, self).__init__(location, base_url,
                                                 *args, **kwargs)

    def path(self, name):
        if not self.location:
            raise ImproperlyConfigured("You're using the staticfiles app "
                                       "without having set the STATIC_ROOT "
                                       "setting to a filesystem path.")
        return super(StaticFilesStorage, self).path(name)


class StaticFileStorage(StaticFilesStorage):

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "The storage backend 'staticfiles.storage.StaticFileStorage' "
            "was renamed to 'staticfiles.storage.StaticFilesStorage'.",
            DeprecationWarning)
        super(StaticFileStorage, self).__init__(*args, **kwargs)


class CachedFilesMixin(object):
    patterns = (
        ("*.css", (
            r"""(url\(['"]{0,1}\s*(.*?)["']{0,1}\))""",
            r"""(@import\s*["']\s*(.*?)["'])""",
        )),
    )

    def __init__(self, *args, **kwargs):
        super(CachedFilesMixin, self).__init__(*args, **kwargs)
        try:
            self.cache = get_cache('staticfiles')
        except (InvalidCacheBackendError, ValueError):
            # Use the default backend
            self.cache = default_cache
        self._patterns = SortedDict()
        for extension, patterns in self.patterns:
            for pattern in patterns:
                compiled = re.compile(pattern)
                self._patterns.setdefault(extension, []).append(compiled)

    def hashed_name(self, name, content=None):
        parsed_name = urlsplit(unquote(name))
        clean_name = parsed_name.path
        if content is None:
            if not self.exists(clean_name):
                raise ValueError("The file '%s' could not be found with %r." %
                                 (clean_name, self))
            try:
                content = self.open(clean_name)
            except IOError:
                # Handle directory paths and fragments
                return name
        path, filename = os.path.split(clean_name)
        root, ext = os.path.splitext(filename)
        # Get the MD5 hash of the file
        md5 = md5_constructor()
        for chunk in content.chunks():
            md5.update(chunk)
        md5sum = md5.hexdigest()[:12]
        hashed_name = os.path.join(path, u"%s.%s%s" %
                                   (root, md5sum, ext))
        unparsed_name = list(parsed_name)
        unparsed_name[2] = hashed_name
        return urlunsplit(unparsed_name)

    def cache_key(self, name):
        return u'staticfiles:cache:%s' % name

    def url(self, name, force=False):
        """
        Returns the real URL in DEBUG mode.
        """
        if settings.DEBUG and not force:
            hashed_name, fragment = name, ''
        else:
            clean_name, fragment = urldefrag(name)
            cache_key = self.cache_key(name)
            hashed_name = self.cache.get(cache_key)
            if hashed_name is None:
                hashed_name = self.hashed_name(clean_name).replace('\\', '/')
                # set the cache if there was a miss
                # (e.g. if cache server goes down)
                self.cache.set(cache_key, hashed_name)

        final_url = super(CachedFilesMixin, self).url(hashed_name)

        # Special casing for a @font-face hack, like url(myfont.eot?#iefix")
        # http://www.fontspring.com/blog/the-new-bulletproof-font-face-syntax
        query_fragment = '?#' in name  # [sic!]
        if fragment or query_fragment:
            urlparts = list(urlsplit(final_url))
            if fragment and not urlparts[4]:
                urlparts[4] = fragment
            if query_fragment and not urlparts[3]:
                urlparts[2] += '?'
            final_url = urlunsplit(urlparts)

        return unquote(final_url)

    def url_converter(self, name):
        """
        Returns the custom URL converter for the given file name.
        """
        def converter(matchobj):
            """
            Converts the matched URL depending on the parent level (`..`)
            and returns the normalized and hashed URL using the url method
            of the storage.
            """
            matched, url = matchobj.groups()
            # Completely ignore http(s) prefixed URLs,
            # fragments and data-uri URLs
            if url.startswith(('#', 'http:', 'https:', 'data:')):
                return matched
            name_parts = name.split(os.sep)
            # Using posix normpath here to remove duplicates
            url = posixpath.normpath(url)
            url_parts = url.split('/')
            parent_level, sub_level = url.count('..'), url.count('/')
            if url.startswith('/'):
                sub_level -= 1
                url_parts = url_parts[1:]
            if parent_level or not url.startswith('/'):
                start, end = parent_level + 1, parent_level
            else:
                if sub_level:
                    if sub_level == 1:
                        parent_level -= 1
                    start, end = parent_level, sub_level - 1
                else:
                    start, end = 1, sub_level - 1
            joined_result = '/'.join(name_parts[:-start] + url_parts[end:])
            hashed_url = self.url(unquote(joined_result), force=True)

            # Return the hashed and normalized version to the file
            return 'url("%s")' % unquote(hashed_url)
        return converter

    def post_process(self, paths, dry_run=False, **options):
        """
        Post process the given list of files (called from collectstatic).

        Processing is actually two separate operations:

        1. renaming files to include a hash of their content for cache-busting,
           and copying those files to the target storage.
        2. adjusting files which contain references to other files so they
           refer to the cache-busting filenames.

        If either of these are performed on a file, then that file is considered
        post-processed.
        """
        # don't even dare to process the files if we're in dry run mode
        if dry_run:
            return

        # delete cache of all handled paths
        self.cache.delete_many([self.cache_key(path) for path in paths])

        # build a list of adjustable files
        matches = lambda path: matches_patterns(path, self._patterns.keys())
        adjustable_paths = [path for path in paths if matches(path)]

        # then sort the files by the directory level
        path_level = lambda name: len(name.split(os.sep))
        for name in sorted(paths.keys(), key=path_level, reverse=True):

            # use the original, local file, not the copied-but-unprocessed
            # file, which might be somewhere far away, like S3
            with paths[name] as original_file:

                # generate the hash with the original content, even for
                # adjustable files.
                hashed_name = self.hashed_name(name, original_file)

                # then get the original's file content..
                if hasattr(original_file, 'seek'):
                    original_file.seek(0)

                hashed_file_exists = self.exists(hashed_name)
                processed = False

                # ..to apply each replacement pattern to the content
                if name in adjustable_paths:
                    content = original_file.read()
                    converter = self.url_converter(name)
                    for patterns in self._patterns.values():
                        for pattern in patterns:
                            content = pattern.sub(converter, content)
                    if hashed_file_exists:
                        self.delete(hashed_name)
                    # then save the processed result
                    content_file = ContentFile(smart_str(content))
                    saved_name = self._save(hashed_name, content_file)
                    hashed_name = force_unicode(saved_name.replace('\\', '/'))
                    processed = True
                else:
                    # or handle the case in which neither processing nor
                    # a change to the original file happened
                    if not hashed_file_exists:
                        processed = True
                        saved_name = self._save(hashed_name, original_file)
                        hashed_name = force_unicode(saved_name.replace('\\', '/'))

                # and then set the cache accordingly
                self.cache.set(self.cache_key(name), hashed_name)
                yield name, hashed_name, processed


class CachedStaticFilesStorage(CachedFilesMixin, StaticFilesStorage):
    """
    A static file system storage backend which also saves
    hashed copies of the files it saves.
    """
    pass


class AppStaticStorage(TimeAwareFileSystemStorage):
    """
    A file system storage backend that takes an app module and works
    for the ``static`` directory of it.
    """
    prefix = None
    source_dir = 'static'

    def __init__(self, app, *args, **kwargs):
        """
        Returns a static file storage if available in the given app.
        """
        # app is the actual app module
        self.app_module = app
        # We special case the admin app here since it has its static files
        # in 'media' for historic reasons.
        if self.app_module == 'django.contrib.admin' and VERSION[:2] < (1, 4):
            self.prefix = 'admin'
            self.source_dir = 'media'
        mod = import_module(self.app_module)
        mod_path = os.path.dirname(mod.__file__)
        location = os.path.join(mod_path, self.source_dir)
        super(AppStaticStorage, self).__init__(location, *args, **kwargs)


class LegacyAppMediaStorage(AppStaticStorage):
    """
    A legacy app storage backend that provides a migration path for the
    default directory name in previous versions of staticfiles, "media".
    """
    source_dir = 'media'


class ConfiguredStorage(LazyObject):
    def _setup(self):
        self._wrapped = get_storage_class(settings.STATICFILES_STORAGE)()

staticfiles_storage = ConfiguredStorage()
