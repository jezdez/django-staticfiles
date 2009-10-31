from django.db import models
from staticfiles import utils
from staticfiles.settings import STORAGE, DIRS
import os


def resolve(path, all=False):
    """
    Find a requested static file, first looking in the static location (if
    local), next in any defined extra media locations and finally in any (non-
    excluded) installed apps.
    
    If ``all`` is ``False`` (default), return the first matching resolved
    absolute path (or ``None`` if no match). Otherwise return a list of
    resolved absolute paths.
    
    """
    matches = []
    
    # Look for the file in the static files storage (if local).
    static_storage = utils.dynamic_import(STORAGE)()
    try:
        static_storage.path('')
    except NotImplementedError:
        pass
    else:
        if static_storage.exists(path):
            matched_path = static_storage.path(path)
            if not all:
                return matched_path
            matches.append(matched_path)
    
    # Next look for the file in the extra media locations.
    for root, prefix in DIRS:
        matched_path = resolve_for_location(root, path, prefix)
        if matched_path:
            if not all:
                return matched_path
            matches.append(matched_path)

    # Finally, look for the file in the apps. 
    for app in models.get_apps():
        app_matches = resolve_for_app(app, path, all=all)
        if app_matches:
            if not all:
                return app_matches
            matches.extend(app_matches)

    return matches


def resolve_for_location(root, path, prefix=None):
    """
    Find a requested static file in a location, returning the resolved
    absolute path (or ``None`` if no match).
    
    """
    if prefix:
        prefix = '%s/' % prefix
        if not path.startswith(prefix):
            return []
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
