==================
django-staticfiles
==================

This is a Django app that provides helpers for serving static files.

The main website for django-staticfiles is
`bitbucket.org/jezdez/django-staticfiles`_ where you can also file tickets.

You can also install the `in-development version`_ of django-staticfiles with
``pip install django-staticfiles==dev`` or ``easy_install django-staticfiles==dev``.

.. _bitbucket.org/jezdez/django-staticfiles: http://bitbucket.org/jezdez/django-staticfiles/
.. _in-development version: http://bitbucket.org/jezdez/django-staticfiles/get/tip.gz#egg=django-staticfiles-dev


Management Commands
===================

build_static
------------

Collects the media files from all installed apps and copies them to the
``STATICFILES_STORAGE``.

You can limit the apps parsed by providing a list of app names::

    $ python manage.py build_static --exclude-dirs admin polls

Duplicate file names are resolved in a similar way to how template resolution
works. Files are initially searched for in STATICFILES_DIRS_ locations,
followed by apps in the order specified by the INSTALLED_APPS setting.

Some commonly used options are:

``--noinput``
  Do NOT prompt the user for input of any kind.
``-i PATTERN`` or ``--ignore=PATTERN``
  Ignore files or directories matching this glob-style pattern. Use multiple
  times to ignore more.
``-n`` or ``--dry-run``
  Do everything except modify the filesystem.
``-l`` or ``--link``
  Create a symbolic link to each file instead of copying.
``--exclude-dirs``
  Exclude additional static locations specified in the ``STATICFILES_DIRS``
  setting.

For a full list of options, refer to the build_static management command help
by running::
 
    $ python manage.py build_static --help

resolve_static
--------------

Resolves one or more expected relative URL path to absolute paths of each media
file on the filesystem. For example::

    $ python manage.py resolve_static css/base.css admin/js/core.css
    /home/special.polls.com/core/media/css/base.css
    /home/polls.com/core/media/css/base.css
    /home/polls.com/src/django/contrib/admin/media/js/core.js

By default, all matching locations are found. To only return the first match
for each relative path, use the ``--first`` option::

    $ python manage.py resolve_static css/base.css --first
    /home/special.polls.com/core/media/css/base.css


static_url context processor
============================

To refer to static file assets from a template, ensure you have set the
STATIC_URL_ setting to the URL path where the static files are served.

Next, add the ``static_url`` context processor to your
``TEMPLATE_CONTEXT_PROCESSORS`` setting::

    TEMPLATE_CONTEXT_PROCESSORS = (
        'staticfiles.context_processors.static_url',
    )

Templates rendered with ``RequestContext`` will now have access to a
``STATIC_URL`` context variable::

    <link href="{{ STATIC_URL }}css/polls.css" rel="stylesheet" type="text/css" />


Serving static files during development
=======================================

.. note:: Don't use this on production servers.
   This feature is **only intended for development**.
   Please, don't shoot yourself in the foot. Thanks.

To serve static media for both ``MEDIA_URL`` and ``STATIC_URL`` add the
following snippet to the end of your primary URL configuration::

    from django.conf import settings
    if settings.DEBUG:
        urlpatterns += patterns('', 
            (r'', include('staticfiles.urls')),
        )


Settings
========

STATIC_ROOT
-----------

:Default: ``''`` (Empty string)

The absolute path to the directory that holds static files like app media::

    STATIC_ROOT = "/home/polls.com/polls/site_media/static/"

This is only used by the default static files storage (i.e. if you use a
different ``STATICFILES_STORAGE``, you don't need to set this).

STATIC_URL
----------

:Default: ``''`` (Empty string)

URL that handles the files served from STATIC_ROOT, e.g.::

    STATIC_URL = '/site_media/static/'

Note that this should **always** have a trailing slash.

STATICFILES_DIRS
----------------

:Default: ``[]``

This setting defines the additional locations the ``staticfiles`` app will
traverse when looking for media files, e.g. if you use the ``build_static``
or ``resolve_static`` management command or use the static file serving view.

It should be defined as a sequence of ``(prefix, path)`` tuples, e.g.::

    STATICFILES_DIRS = (
        ('', '/home/special.polls.com/polls/media'),
        ('', '/home/polls.com/polls/media'),
        ('common', '/opt/webfiles/common'),
    )

STATICFILES_PREPEND_LABEL_APPS
-------------------------------

:Default: ``('django.contrib.admin',)``

A sequence of app paths that should be prefixed with the label name.
For example, ``django.contrib.admin`` media files should be served from
``admin/[js,css,images]`` rather than the media files getting served directly
from the static root.

STATICFILES_MEDIA_DIRNAMES
--------------------------

:Default: ``('media',)``

A sequence of directory names to be used when searching for media files in
installed apps, e.g. if an app has its media files in ``<app>/static``
use::

    STATICFILES_MEDIA_DIRNAMES = (
        'media',
        'static',
    )

STATICFILES_EXCLUDED_APPS
-------------------------

:Default: ``[]``

A sequence of app paths that should be ignored when searching for media
files::

    STATICFILES_EXCLUDED_APPS = (
        'annoying.app',
        'old.company.app',
    )

STATICFILES_STORAGE
-------------------

:Default: ``'staticfiles.storage.StaticFileStorage'``

The storage to use for copying static files to a single location. 


Changelog
=========

v0.2.0 (2009-11-25):
--------------------

* Renamed build_media and resolve_media management commands to build_static
  and resolve_media to avoid confusions between Django's use of the term
  "media" (for uploads) and "static" files.

* Rework most of the internal logic, abstracting the core functionality away
  from the management commands.

* Use file system storage backend by default, ability to override it with
  custom storage backend

* Removed --interactive option to streamline static file resolving.

* Added extensive tests

* Uses standard logging

v0.1.2 (2009-09-02):
--------------------

* Fixed a typo in settings.py

* Fixed a conflict in build_media (now build_static) between handling
  non-namespaced app media and other files with the same relative path.

v0.1.1 (2009-09-02):
--------------------

* Added README with a bit of documentation :)

v0.1.0 (2009-09-02):
--------------------

* Initial checkin from Pinax' source.

* Will create the STATIC_ROOT directory if not existent.
