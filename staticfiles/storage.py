from django.conf import settings
from django.core.files.storage import FileSystemStorage


class StaticFileStorage(FileSystemStorage):
    """
    Standard file system storage for static files.
    
    The defaults for ``location`` and ``base_url`` are ``STATIC_ROOT`` and
    ``STATIC_URL``.
    
    """
    def __init__(self, location=None, base_url=None, *args, **kwargs):
        if location is None:
            location = settings.STATIC_ROOT
        if base_url is None:
            base_url = settings.STATIC_URL
        super(StaticFileStorage, self).__init__(location, base_url,
                                                *args, **kwargs)
