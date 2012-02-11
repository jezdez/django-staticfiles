import os
import fnmatch
import warnings


def get_files_for_app(app, ignore_patterns=None):
    """
    Return a list containing the relative source paths for all files that
    should be copied for an app.
    """
    from staticfiles.storage import AppStaticStorage
    if ignore_patterns is None:
        ignore_patterns = []
    warnings.warn(
        "The staticfiles.utils.get_files_for_app utility function is "
        "deprecated. Use staticfiles.storage.AppStaticStorage.get_files "
        "instead.", DeprecationWarning)
    return AppStaticStorage(app).get_files(ignore_patterns)

def get_app_prefix(app):
    """
    Return the path name that should be prepended to files for this app.
    """
    from staticfiles.storage import AppStaticStorage
    warnings.warn(
        "The staticfiles.utils.get_app_prefix utility function is "
        "deprecated. Use staticfiles.storage.AppStaticStorage.get_prefix "
        "instead.", DeprecationWarning)
    return AppStaticStorage(app).get_prefix()

def matches_patterns(path, patterns=None):
    """
    Return True or False depending on whether the ``path`` should be
    ignored (if it matches any pattern in ``ignore_patterns``).
    """
    if patterns is None:
        patterns = []
    for pattern in patterns:
        if fnmatch.fnmatchcase(path, pattern):
            return True
    return False

def get_filtered_patterns(storage, ignore_patterns=None, location=''):
    """
    Return a filtered list of patterns that match the storage location.
    """
    if ignore_patterns is None:
        ignore_patterns = []
    storage_prefix = getattr(storage, 'prefix', None) or ''
    if location:
        rel_location = os.path.join(storage_prefix, location)
        abs_location = os.path.join(storage.location, location)
    else:
        rel_location = storage_prefix
        abs_location = storage.location
    ignore_filtered = []
    for pattern in ignore_patterns:
        head, tail = os.path.split(pattern)
        if not tail:
            head, tail = os.path.split(head)
        if head in ('', rel_location, abs_location):
            ignore_filtered.append(tail)
    return ignore_filtered

def get_files(storage, ignore_patterns=None, location=''):
    """
    Recursively walk the storage directories yielding the paths
    of all files that should be copied.
    """
    if ignore_patterns is None:
        ignore_patterns = []
    ignore_filtered = get_filtered_patterns(storage, ignore_patterns, location)
    directories, files = storage.listdir(location)
    for fn in files:
        if matches_patterns(fn, ignore_filtered):
            continue
        if location:
            fn = os.path.join(location, fn)
        yield fn
    for dir in directories:
        if matches_patterns(dir, ignore_filtered):
            continue
        if location:
            dir = os.path.join(location, dir)
        for fn in get_files(storage, ignore_patterns, dir):
            yield fn

