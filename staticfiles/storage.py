import os
import warnings
from datetime import datetime

from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module
from django.utils.functional import LazyObject

from staticfiles.conf import settings


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
        if not location:
            raise ImproperlyConfigured("You're using the staticfiles app "
                "without having set the STATIC_ROOT setting.")
        # check for None since we might use a root URL (``/``)
        if base_url is None:
            raise ImproperlyConfigured("You're using the staticfiles app "
                "without having set the STATIC_URL setting.")
        super(StaticFilesStorage, self).__init__(location, base_url, *args, **kwargs)


class StaticFileStorage(StaticFilesStorage):

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "The storage backend 'staticfiles.storage.StaticFileStorage' "
            "was renamed to 'staticfiles.storage.StaticFilesStorage'.",
            PendingDeprecationWarning)
        super(StaticFileStorage, self).__init__(*args, **kwargs)


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
        if self.app_module == 'django.contrib.admin':
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

