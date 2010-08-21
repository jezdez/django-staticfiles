Management Commands
===================

.. highlight:: console

.. _build_static:

build_static
------------

Collects the media files from all installed apps and copies them to the
:ref:`staticfiles-storage`.

You can limit the apps parsed by providing a list of app names::

   $ python manage.py build_static --exclude-dirs admin polls

Duplicate file names are resolved in a similar way to how template resolution
works. Files are initially searched for in :ref:`staticfiles-dirs` locations,
followed by apps in the order specified by the INSTALLED_APPS setting.

Some commonly used options are:

- ``--noinput``
    Do NOT prompt the user for input of any kind.

- ``-i PATTERN`` or ``--ignore=PATTERN``
    Ignore files or directories matching this glob-style pattern. Use multiple
    times to ignore more.

- ``-n`` or ``--dry-run``
    Do everything except modify the filesystem.

- ``-l`` or ``--link``
    Create a symbolic link to each file instead of copying.

- ``--exclude-dirs``
    Exclude additional static locations specified in the
    :ref:`STATICFILES_DIRS setting <staticfiles-dirs>`.

For a full list of options, refer to the build_static management command help
by running::

   $ python manage.py build_static --help

.. _resolve_static:

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
