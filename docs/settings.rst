Settings
========

.. currentmodule:: django.conf.settings

.. attribute:: STATIC_ROOT

    :default: ``""`` (Empty string)

    The absolute path to the directory that contains static content after
    using :ref:`collectstatic`.

    Example: ``"/home/example.com/static/"``

    When using the :ref:`collectstatic` management command this will be used
    to collect static files into, to be served under the URL specified as
    :attr:`~django.conf.settings.STATIC_URL`.

    This is a **required setting** to use :ref:`collectstatic` -- unless
    you've overridden :attr:`~django.conf.settings.STATICFILES_STORAGE` and
    are using a custom storage backend.

    .. warning::

      This is not a place to store your static files permanently
      under version control!

      You should do that in directories that will be found by your
      :attr:`~django.conf.settings.STATICFILES_FINDERS` (by default,
      per-app ``'static'`` subdirectories, and any directories you
      include in :attr:`~django.conf.settings.STATICFILES_DIRS` setting).
      Files from those locations will be collected into
      :attr:`~django.conf.settings.STATIC_ROOT`.

    See also :attr:`~django.conf.settings.STATIC_URL`.

.. attribute:: STATIC_URL

    :default: ``None``

    URL that handles the files served from ``STATIC_ROOT`` and used by
    ``runserver`` in development mode (when ``DEBUG = True``).

    Example: ``"/site_media/static/"`` or ``"http://static.example.com/"``

    It must end in a slash if set to a non-empty value.

    See also :attr:`~django.conf.settings.STATIC_ROOT`.

.. attribute:: STATICFILES_DIRS

    :default: ``()``

    This setting defines the additional locations the staticfiles app will
    traverse if the :class:`FileSystemFinder` finder is enabled, e.g. if you
    use the :ref:`collectstatic` or :ref:`findstatic` management command or
    use the static file serving view.

    This should be set to a list or tuple of strings that contain full paths
    to your additional files directory(ies) e.g.::

        STATICFILES_DIRS = (
            "/home/special.polls.com/polls/static",
            "/home/polls.com/polls/static",
            "/opt/webfiles/common",
        )

    In case you want to refer to files in one of the locations with an
    additional namespace, you can **OPTIONALLY** provide a prefix as
    ``(prefix, path)`` tuples, e.g.::

        STATICFILES_DIRS = (
            # ...
            ("downloads", "/opt/webfiles/stats"),
        )

    Example:

    Assuming you have :attr:`~django.conf.settings.STATIC_URL` set
    ``'/static/'``, the :ref:`collectstatic` management command would collect
    the stats files in a ``'downloads'`` subdirectory of
    :attr:`~django.conf.settings.STATIC_ROOT`.

    This would allow you to refer to the local file
    ``'/opt/webfiles/stats/polls_20101022.tar.gz'`` with
    ``'/static/downloads/polls_20101022.tar.gz'`` in your templates, e.g.:

    .. code-block:: django

        <a href="{{ STATIC_URL }}downloads/polls_20101022.tar.gz">


.. attribute:: STATICFILES_IGNORE_PATTERNS

    :Default: ``()``

    This setting defines patterns to be ignored by the :ref:`collectstatic`
    management command.

    This should be set to a list or tuple of strings that contain file or
    directory names and may include an absolute file system path or a path
    relative to :attr:`~django.conf.settings.STATIC_ROOT`, e.g.::

        STATICFILES_IGNORE_PATTERNS = (
            "*.txt",
            "tests",
            "css/*.old",
            "/opt/webfiles/common/*.txt",
            "/opt/webfiles/common/temp",
        )

    .. versionadded:: 1.2

.. attribute:: STATICFILES_EXCLUDED_APPS

    :default: ``()``

    A sequence of app paths that should be ignored when searching for static
    files, e.g.::

        STATICFILES_EXCLUDED_APPS = (
            'annoying.app',
            'old.company.app',
        )

.. attribute:: STATICFILES_STORAGE

    :default: ``'staticfiles.storage.StaticFileStorage'``

    The file storage engine to use when collecting static files with the
    :ref:`collectstatic` management command.

.. attribute:: STATICFILES_FINDERS

    :default: ``('staticfiles.finders.FileSystemFinder',
                 'staticfiles.finders.AppDirectoriesFinder')``

    The list of finder backends that know how to find static files in
    various locations.

    The default will find files stored in the
    :attr:`~django.conf.settings.STATICFILES_DIRS` setting
    (using :class:`staticfiles.finders.FileSystemFinder`) and in a
    ``static`` subdirectory of each app (using
    :class:`staticfiles.finders.AppDirectoriesFinder`)

    One finder is disabled by default:
    :class:`staticfiles.finders.DefaultStorageFinder`. If added to
    your :attr:`~django.conf.settings.STATICFILES_FINDERS` setting, it will
    look for static files in the default file storage as defined by the
    ``DEFAULT_FILE_STORAGE`` setting.

    .. note::

        When using the ``AppDirectoriesFinder`` finder, make sure your apps
        can be found by staticfiles. Simply add the app to the
        ``INSTALLED_APPS`` setting of your site.

    Static file finders are currently considered a private interface, and this
    interface is thus undocumented.

    To ease the burden of upgrading a Django project from a
    non-``staticfiles`` setup, the optional finder backend
    :class:`staticfiles.finders.LegacyAppDirectoriesFinder` is shipped as
    part of ``django-staticfiles``.

    When added to the :attr:`~django.conf.settings.STATICFILES_FINDERS`
    setting, it'll enable ``staticfiles`` to use the ``media`` directory of
    the apps in ``INSTALLED_APPS``, similarly
    :class:`staticfiles.finders.AppDirectoriesFinder`.

    This is especially useful for 3rd party apps that haven't been switched
    over to the ``static`` directory instead. If you want to use both
    ``static`` **and** ``media``, don't forget to have
    :class:`staticfiles.finders.AppDirectoriesFinder` in the
    :attr:`~django.conf.settings.STATICFILES_FINDERS`, too.
