import os
from django.db import models
from staticfiles import utils
from staticfiles.settings import STORAGE, DIRS


def resolve(path, all=False):
    """
    Find a requested static file, first looking in any defined extra media
    locations and next in any (non-excluded) installed apps.
    
    If no matches are found and the static location is local, look for a match
    there too.
    
    If ``all`` is ``False`` (default), return the first matching resolved
    absolute path (or ``None`` if no match). Otherwise return a list of
    resolved absolute paths.
    
    """
    matches = []
    
    # First look for the file in the extra media locations.
    for root in DIRS:
        if isinstance(root, (list, tuple)):
            prefix, root = root
        else:
            prefix = ''
        matched_path = resolve_for_location(root, path, prefix)
        if matched_path:
            if not all:
                return matched_path
            matches.append(matched_path)

    # Next, look for the file in the apps. 
    for app in models.get_apps():
        app_matches = resolve_for_app(app, path, all=all)
        if app_matches:
            if not all:
                return app_matches
            matches.extend(app_matches)

    if matches:
        return matches

    # No match was found yet, look for the file in the static files storage (if
    # local).
    static_storage = utils.dynamic_import(STORAGE)()
    try:
        static_storage.path('')
    except NotImplementedError:
        pass
    else:
        if static_storage.exists(path):
            match = static_storage.path(path)
            if all:
                match = [match]
            return match

    # No match.
    return all and [] or None


def resolve_for_location(root, path, prefix=None):
    """
    Find a requested static file in a location, returning the resolved
    absolute path (or ``None`` if no match).
    
    """
    if prefix:
        prefix = '%s/' % prefix
        if not path.startswith(prefix):
            return None
        path = path[len(prefix):]
    path = os.path.join(root, path)
    if os.path.exists(path):
        return path


def resolve_for_app(app, path, all=False):
    """
    Find a requested static file in an app's media locations.
    
    If ``all`` is ``False`` (default), return the first matching resolved
    absolute path (or ``None`` if no match). Otherwise return a list of
    resolved absolute paths.
    
    """
    prefix = utils.get_app_prefix(app)
    if prefix:
        prefix = '%s/' % prefix
        if not path.startswith(prefix):
            return []
        path = path[len(prefix):]
    paths = []
    for storage in utils.app_static_storages(app):
        if storage.exists(path):
            matched_path = storage.path(path)
            if not all:
                return matched_path
            paths.append(matched_path)
    return paths
