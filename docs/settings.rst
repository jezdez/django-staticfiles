Settings
========

``STATIC_ROOT``
---------------

:Default: ``''`` (Empty string)

The absolute path to the directory that holds static files like app media::

    STATIC_ROOT = "/home/polls.com/polls/site_media/static/"

This is only used by the default static files storage (i.e. if you use a
different ``STATICFILES_STORAGE``, you don't need to set this).

.. _static-url:

``STATIC_URL``
--------------

:Default: ``''`` (Empty string)

URL that handles the files served from STATIC_ROOT, e.g.::

    STATIC_URL = '/site_media/static/'

Note that this should **always** have a trailing slash.

.. _staticfiles-dirs:

``STATICFILES_DIRS``
--------------------

:Default: ``[]``

This setting defines the additional locations the ``staticfiles`` app will
traverse when looking for media files, e.g. if you use the :ref:`build_static`
or :ref:`resolve_static` management command or use the static file serving
view.

It should be defined as a sequence of ``(prefix, path)`` tuples, e.g.::

    STATICFILES_DIRS = (
        ('', '/home/special.polls.com/polls/media'),
        ('', '/home/polls.com/polls/media'),
        ('common', '/opt/webfiles/common'),
    )

``STATICFILES_EXCLUDED_APPS``
-----------------------------

:Default: ``[]``

A sequence of app paths that should be ignored when searching for media
files::

    STATICFILES_EXCLUDED_APPS = (
        'annoying.app',
        'old.company.app',
    )

.. _staticfiles-storage:

``STATICFILES_STORAGE``
-----------------------

:Default: ``'staticfiles.storage.StaticFileStorage'``

The storage to use for copying static files to a single location. 


``STATICFILES_RESOLVERS``
-------------------------

:Default: ``('staticfiles.resolvers.FileSystemResolver',
             'staticfiles.resolvers.AppDirectoriesResolver',
             'staticfiles.resolvers.LocalStorageResolver')``

The list of resolver classes that know how to find static files in
various locations.

If you know you only keep your files in one of those
locations, just omit the unnecessary resolvers.


