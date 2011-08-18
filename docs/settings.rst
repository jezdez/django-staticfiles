Settings
========

.. _STATIC_ROOT:

``STATIC_ROOT``
---------------

:Default: ``''`` (Empty string)

The absolute path to the directory that contains static content after using
:ref:`collectstatic`.

Example: ``"/home/example.com/static/"``

When using the :ref:`collectstatic` management command this will be used to
collect static files into, to be served under the URL specified as
STATIC_URL_.

This is a **required setting** to use :ref:`collectstatic` -- unless you've
overridden STATICFILES_STORAGE_ and are using a custom storage backend.

.. warning:: This is not a place to store your static files permanently under
  version control; you should do that in directories that will be found by
  your STATICFILES_FINDERS_ (by default, per-app ``'static'`` subdirectories,
  and any directories you include in STATICFILES_DIRS_ setting). Files from
  those locations will be collected into STATIC_ROOT_.

See also STATIC_URL_.

.. _STATIC_URL:

``STATIC_URL``
--------------

:Default: ``None``

URL that handles the files served from ``STATIC_ROOT`` and used by
``runserver`` in development mode (when ``DEBUG = True``).

Example: ``"/site_media/static/"`` or ``"http://static.example.com/"``

It must end in a slash if set to a non-empty value.

See also STATIC_ROOT_.

.. _STATICFILES_DIRS:

``STATICFILES_DIRS``
--------------------

:Default: ``[]``

This setting defines the additional locations the staticfiles app will traverse
if the :class:`FileSystemFinder` finder is enabled, e.g. if you use the
:ref:`collectstatic` or :ref:`findstatic` management command or use the
static file serving view.

This should be set to a list or tuple of strings that contain full paths to
your additional files directory(ies) e.g.::

    STATICFILES_DIRS = (
        "/home/special.polls.com/polls/static",
        "/home/polls.com/polls/static",
        "/opt/webfiles/common",
    )

Prefixes (optional)
"""""""""""""""""""

In case you want to refer to files in one of the locations with an additional
namespace, you can **OPTIONALLY** provide a prefix as ``(prefix, path)``
tuples, e.g.::

    STATICFILES_DIRS = (
        # ...
        ("downloads", "/opt/webfiles/stats"),
    )

Example:

Assuming you have STATIC_URL_ set ``'/static/'``, the :ref:`collectstatic`
management command would collect the stats files in a ``'downloads'``
subdirectory of STATIC_ROOT_.

This would allow you to refer to the local file
``'/opt/webfiles/stats/polls_20101022.tar.gz'`` with
``'/static/downloads/polls_20101022.tar.gz'`` in your templates, e.g.::

    <a href="{{ STATIC_URL }}downloads/polls_20101022.tar.gz">

``STATICFILES_EXCLUDED_APPS``
-----------------------------

:Default: ``[]``

A sequence of app paths that should be ignored when searching for static
files::

    STATICFILES_EXCLUDED_APPS = (
        'annoying.app',
        'old.company.app',
    )

.. _STATICFILES_STORAGE:

``STATICFILES_STORAGE``
-----------------------

:Default: ``'staticfiles.storage.StaticFileStorage'``

The file storage engine to use when collecting static files with the
:ref:`collectstatic` management command.


``STATICFILES_FINDERS``
-----------------------

:Default: ``('staticfiles.finders.FileSystemFinder',
             'staticfiles.finders.AppDirectoriesFinder')``

The list of finder backends that know how to find static files in
various locations.

The default will find files stored in the STATICFILES_DIRS_ setting
(using :class:`staticfiles.finders.FileSystemFinder`) and in a
``static`` subdirectory of each app (using
:class:`staticfiles.finders.AppDirectoriesFinder`)

One finder is disabled by default:
:class:`staticfiles.finders.DefaultStorageFinder`. If added to
your STATICFILES_FINDERS_ setting, it will look for static files in
the default file storage as defined by the ``DEFAULT_FILE_STORAGE``
setting.

.. note::

    When using the ``AppDirectoriesFinder`` finder, make sure your apps
    can be found by staticfiles. Simply add the app to the
    ``INSTALLED_APPS`` setting of your site.

Static file finders are currently considered a private interface, and this
interface is thus undocumented.

Legacy 'media' dir finder (optional)
""""""""""""""""""""""""""""""""""""

To ease the burden of upgrading a Django project from a non-``staticfiles``
setup, the optional finder backend
:class:`staticfiles.finders.LegacyAppDirectoriesFinder` is shipped as part of
``django-staticfiles``. When added to the STATICFILES_FINDERS_ setting, it'll
enable ``staticfiles`` to use the ``media`` directory of the apps in
``INSTALLED_APPS``, similarly
:class:`staticfiles.finders.AppDirectoriesFinder`.

This is especially useful for 3rd party apps that haven't been switched over
to the ``static`` directory instead. If you want to use both ``static``
**and** ``media``, don't forget to have
:class:`staticfiles.finders.AppDirectoriesFinder` in the
STATICFILES_FINDERS_, too.
