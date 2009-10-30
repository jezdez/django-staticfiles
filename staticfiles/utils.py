import os
import sys

from staticfiles.settings import ROOT, DIRS, MEDIA_DIRNAMES, APPS


def get_media_path(path, all=False):
    """
    Traverses the following locations to find a requested media file in the
    given order and return the absolute file path:

    1. The site media path, e.g. for user-contributed files, e.g.:
        <project>/site_media/static/<path>
    2. Any extra media locations given in the settings
    4. Installed apps:
        a) <app>/media/<app>/<path>
        b) <app>/media/<path>
    """
    collection = []
    locations = [ROOT] + [root for label, root in DIRS]
    for location in locations:
        media = os.path.join(location, path)
        if os.path.exists(media):
            if not all:
                return media
            collection.append(media)

    installed_apps = APPS
    app_labels = [label.split('.')[-1] for label in installed_apps]
    for app in installed_apps:
        app_mod = import_module(app)
        app_root = os.path.dirname(app_mod.__file__)
        for media_dir in MEDIA_DIRNAMES:
            media = os.path.join(app_root, media_dir, path)
            if os.path.exists(media):
                if not all:
                    return media
                collection.append(media)
            splitted_path = path.split('/', 1)
            if len(splitted_path) > 1:
                app_name, newpath = splitted_path
                if app_name in app_labels:
                    media = os.path.join(app_root, media_dir, newpath)
                    if os.path.exists(media):
                        if not all:
                            return media
                        collection.append(media)
    return collection or None


def _resolve_name(name, package, level):
    """Return the absolute name of the module to be imported."""
    if not hasattr(package, 'rindex'):
        raise ValueError("'package' not set to a string")
    dot = len(package)
    for x in xrange(level, 1, -1):
        try:
            dot = package.rindex('.', 0, dot)
        except ValueError:
            raise ValueError("attempted relative import beyond top-level "
                              "package")
    return "%s.%s" % (package[:dot], name)


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
