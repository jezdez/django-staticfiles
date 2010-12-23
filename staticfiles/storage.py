import warning

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ImproperlyConfigured

from staticfiles import utils
from staticfiles.settings import URL as STATIC_URL, ROOT as STATIC_ROOT

class StaticFilesStorage(FileSystemStorage):
    """
    Standard file system storage for site media files.
    
    The defaults for ``location`` and ``base_url`` are
    ``STATIC_ROOT`` and ``STATIC_URL``.
    """
    def __init__(self, location=None, base_url=None, *args, **kwargs):
        if location is None:
            location = STATIC_ROOT
        if base_url is None:
            base_url = STATIC_URL
        if not location:
            raise ImproperlyConfigured("You're using the staticfiles app "
                "without having set the STATIC_ROOT setting. Set it to "
                "the absolute path of the directory that holds static media.")
        # check for None since we might use a root URL (``/``)
        if base_url is None:
            raise ImproperlyConfigured("You're using the staticfiles app "
                "without having set the STATIC_URL setting. Set it to "
                "URL that handles the files served from STATIC_ROOT.")
        if settings.DEBUG:
            utils.check_settings()
        super(StaticFilesStorage, self).__init__(location, base_url,
                                                 *args, **kwargs)

class StaticFileStorage(StaticFilesStorage):

    def __init__(self, *args, **kwargs):
        warning.warn(
            "The storage backend 'staticfiles.storage.StaticFileStorage' "
            "was renamed to 'staticfiles.storage.StaticFilesStorage'.")
        super(StaticFileStorage, self).__init__(*args, **kwargs)

