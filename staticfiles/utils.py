import os
import sys
import fnmatch
import warnings

from django.conf import settings


def get_files_for_app(app, ignore_patterns=[]):
    """
    Return a list containing the relative source paths for all files that
    should be copied for an app.
    """
    from staticfiles.storage import AppStaticStorage
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

def get_files(storage, ignore_patterns=None, location=''):
    """
    Recursively walk the storage directories yielding the paths
    of all files that should be copied.
    """
    if ignore_patterns is None:
        ignore_patterns = []
    directories, files = storage.listdir(location)
    for fn in files:
        if matches_patterns(fn, ignore_patterns):
            continue
        if location:
            fn = os.path.join(location, fn)
        yield fn
    for dir in directories:
        if matches_patterns(dir, ignore_patterns):
            continue
        if location:
            dir = os.path.join(location, dir)
        for fn in get_files(storage, ignore_patterns, dir):
            yield fn


class AppSettingsOptions(object):

    def __init__(self, meta, *args, **kwargs):
        self.configured = False

    def prefixed_name(self, name):
        if name.startswith(self.app_label):
            return name
        return "%s_%s" % (self.app_label.upper(), name.upper())


class AppSettingsMetaClass(type):
    options_class = AppSettingsOptions

    def __new__(cls, name, bases, attrs):
        super_new = super(AppSettingsMetaClass, cls).__new__
        parents = [b for b in bases if isinstance(b, AppSettingsMetaClass)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        try:
            meta = attrs.pop('Meta')
        except KeyError:
            meta = None

        attrs['_meta'] = cls.options_class(meta)
        new_class = super_new(cls, name, bases, attrs)

        if getattr(new_class._meta, 'app_label', None) is None:
            # Figure out the app_label by looking one level up.
            # For 'django.contrib.sites.models', this would be 'sites'.
            model_module = sys.modules[new_class.__module__]
            new_class._meta.app_label = model_module.__name__.split('.')[-2]

        names = []
        defaults = []
        for name in filter(lambda name: name == name.upper(), attrs):
            prefixed_name = new_class._meta.prefixed_name(name)
            names.append((name, prefixed_name))
            defaults.append((prefixed_name, attrs.pop(name)))

        new_class.defaults = dict(defaults)
        new_class.names = dict(names)
        new_class._configure()

    def _configure(cls):
        if not cls._meta.configured:
            # the ad-hoc settings class instance used to configure each value
            obj = cls()
            for name, prefixed_name in obj.names.items():
                default_value = obj.defaults.get(prefixed_name)
                value = getattr(settings, prefixed_name, default_value)
                callback = getattr(obj, "configure_%s" % name.lower(), None)
                if callable(callback):
                    value = callback(value)
                # Finally, set the setting in the global setting object
                setattr(settings, prefixed_name, value)
            cls._meta.configured = True


class AppSettings(object):
    """
    An app setting object to be used for handling app setting defaults
    gracefully and providing a nice API for them. Say you have an app
    called ``myapp`` and want to define a few defaults, and refer to the
    defaults easily in the apps code. Add a ``settings.py`` to your app's
    models.py::

        from path.to.utils import AppSettings

        class MyAppSettings(AppSettings):
            SETTING_1 = "one"
            SETTING_2 = (
                "two",
            )

            class Meta:
                app_label = 'myapp'

    The settings are initialized with the app label of where the setting is
    located at. E.g. if your ``models.py`` is in the ``myapp`` package,
    the prefix of the settings will be ``MYAPP``.

    The ``MyAppSettings`` class will automatically look at Django's
    global setting to determine each of the settings. E.g. adding this to
    your site's ``settings.py`` will set the ``SETTING_1`` app setting
    accordingly::

        MYAPP_SETTING_1 = "uno"

    Usage
    -----

    Instead of using ``from django.conf import settings`` as you would
    usually do, you can **optionally** switch to using your apps own
    settings module to access the settings::

        from myapp.models import MyAppSettings

        myapp_settings = MyAppSettings()

        print myapp_settings.MYAPP_SETTING_1

    ``AppSettings`` class automatically work as proxies for the other
    settings, which aren't related to the app. For example the following
    code is perfectly valid::

        from myapp.models import MyAppSettings

        settings = MyAppSettings()

        if "myapp" in settings.INSTALLED_APPS:
            print "yay, myapp is installed!"

    In case you want to set some settings ad-hoc, you can simply pass
    the value when instanciating the ``AppSettings`` class::

        from myapp.models import MyAppSettings

        settings = MyAppSettings(SETTING_1='something completely different')

        if 'different' in settings.MYAPP_SETTINGS_1:
            print 'yay, I'm different!'

    Custom handling
    ---------------

    Each of the settings can be individually configured with callbacks.
    For example, in case a value of a setting depends on other settings
    or other dependencies. The following example sets one setting to a
    different value depending on a global setting::

        from django.conf import settings

        class MyCustomAppSettings(AppSettings):
            ENABLED = True

            def configure_enabled(self, value):
                return value and not self.DEBUG

    The value of ``MYAPP_ENABLED`` will vary depending on the
    value of the global ``DEBUG`` setting.

    Each of the app settings can be customized by providing
    a method ``configure_<lower_setting_name>`` that takes the default
    value as defined in the class attributes as the only parameter.
    The method needs to return the value to be use for the setting in
    question.
    """
    __metaclass__ = AppSettingsMetaClass

    def __init__(self, **kwargs):
        for name, value in kwargs.iteritems():
            setattr(self, self._meta.prefixed_name(name), value)

    def __dir__(self):
        return sorted(list(set(dir(settings))))

    __members__ = lambda self: self.__dir__()

    def __getattr__(self, name):
        return getattr(settings, name)

    def __setattr__(self, name, value):
        setattr(settings, name, value)
