import os
import fnmatch
from django.core.files.storage import FileSystemStorage
from staticfiles.settings import MEDIA_DIRNAMES, PREPEND_LABEL_APPS, \
    EXCLUDED_APPS

def get_files_for_app(app, ignore_patterns=[]):
    """
    Return a list containing the relative source paths for all files that
    should be copied for an app.
    
    """
    prefix = get_app_prefix(app)
    files = []
    for storage in app_static_storages(app):
        for path in get_files(storage, ignore_patterns):
            if prefix:
                path = '/'.join([prefix, path])
            files.append(path)
    return files


def app_static_storages(app):
    """
    A generator which yields the potential static file storages for an app.
    
    Excluded apps do not yield any storages
    
    Only storages for valid locations are yielded.
    
    """
    # "app" is actually the models module of the app. Remove the '.models'. 
    app_module = '.'.join(app.__name__.split('.')[:-1])
    if app_module in EXCLUDED_APPS:
        return
    # The models module may be a package in which case dirname(app.__file__)
    # would be wrong. Import the actual app as opposed to the models module.
    app = dynamic_import(app_module) 
    app_root = os.path.dirname(app.__file__)
    for media_dirname in MEDIA_DIRNAMES:
        location = os.path.join(app_root, media_dirname)
        if not os.path.isdir(location):
            continue
        yield FileSystemStorage(location=location)


def get_app_prefix(app):
    """
    Return the path name that should be prepended to files for this app.
    
    """
    # "app" is actually the models module of the app. Remove the '.models'. 
    bits = app.__name__.split('.')[:-1]
    app_name = bits[-1]
    app_module = '.'.join(bits)
    if app_module in PREPEND_LABEL_APPS:
        return app_name


def get_files(storage, ignore_patterns=[], location=''):
    """
    Recursively walk the storage directories gathering a complete list of files
    that should be copied, returning this list.
    
    """

    def is_ignored(path):
        """
        Return True or False depending on whether the ``path`` should be
        ignored (if it matches any pattern in ``ignore_patterns``).
        
        """
        for pattern in ignore_patterns:
            if fnmatch.fnmatchcase(path, pattern):
                return True
        return False

    directories, files = storage.listdir(location)
    static_files = [location and '/'.join([location, fn]) or fn
                    for fn in files
                    if not is_ignored(fn)]
    for dir in directories:
        if is_ignored(dir):
            continue
        if location:
            dir = '/'.join([location, dir])
        static_files.extend(get_files(storage, ignore_patterns, dir))
    return static_files


def dynamic_import(import_string):
    """
    Dynamically import a module or object.
    
    """
    # Use rfind rather than rsplit for Python 2.3 compatibility.
    lastdot = import_string.rfind('.')
    if lastdot == -1:
        return __import__(import_string, {}, {}, [])
    module_name, attr = import_string[:lastdot], import_string[lastdot + 1:]
    parent_module = __import__(module_name, {}, {}, [attr])
    return getattr(parent_module, attr)
