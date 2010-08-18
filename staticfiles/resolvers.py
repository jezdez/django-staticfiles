import os
from django.core.files.storage import get_storage_class
from django.db import models
from django.core.exceptions import ImproperlyConfigured
from django.utils.importlib import import_module

from staticfiles import settings, utils

class BaseResolver(object):

    def resolve(self, path, all=False):
        """
        Given a relative file path this ought to find an
        absolute file path.

        If the ``all`` parameter is ``False`` (default) only
        the first found file path will be returned; if set
        to ``True`` a list of all found files paths is returned.
        """
        raise NotImplementedError


class FileSystemResolver(BaseResolver):

    def resolve(self, path, all=False):
        """
        Looks for files in the extra media locations
        as defined in ``STATICFILES_DIRS``.
        """
        matches = []
        for root in settings.DIRS:
            if isinstance(root, (list, tuple)):
                prefix, root = root
            else:
                prefix = ''
            matched_path = self.resolve_for_location(root, path, prefix)
            if matched_path:
                if not all:
                    return matched_path
                matches.append(matched_path)
        return matches

    def resolve_for_location(self, root, path, prefix=None):
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


class AppDirectoriesResolver(BaseResolver):

    def resolve(self, path, all=False):
        """
        Looks for files in the app directories.
        """
        matches = []
        for app in models.get_apps():
            app_matches = self.resolve_for_app(app, path, all=all)
            if app_matches:
                if not all:
                    return app_matches
                matches.extend(app_matches)
        return matches

    def resolve_for_app(self, app, path, all=False):
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


class LocalStorageResolver(BaseResolver):
    static_storage = get_storage_class(settings.STORAGE)()

    def resolve(self, path, all=False):
        """
        Last resort, looks for files in the
        static files storage if it's local.
        """
        try:
            self.static_storage.path('')
        except NotImplementedError:
            pass
        else:
            if self.static_storage.exists(path):
                match = self.static_storage.path(path)
                if all:
                    match = [match]
                return match
        return []


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
    for resolver_path in settings.RESOLVERS:
        resolver = get_resolver(resolver_path)()
        result = resolver.resolve(path, all=all)
        if not all and result:
            return result
        if not isinstance(result, (list, tuple)):
            result = [result]
        matches.extend(result)

    if matches:
        return matches

    # No match.
    return all and [] or None


def get_resolver(import_path):
    """
    Imports the message storage class described by import_path, where
    import_path is the full Python path to the class.
    """
    try:
        dot = import_path.rindex('.')
    except ValueError:
        raise ImproperlyConfigured("%s isn't a Python path." % import_path)
    module, classname = import_path[:dot], import_path[dot + 1:]
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing module %s: "%s"' %
                                   (module, e))
    try:
        cls = getattr(mod, classname)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define a "%s" '
                                   'class.' % (module, classname))
    if not issubclass(cls, BaseResolver):
        raise ImproperlyConfigured('Resolver "%s" is not a subclass of "%s"' %
                                   (cls, BaseResolver))
    return cls
