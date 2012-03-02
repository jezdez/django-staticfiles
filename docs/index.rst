.. include:: ../README.rst

Differences to ``django.contrib.staticfiles``
---------------------------------------------

Features of ``django-staticfiles`` which Django's ``staticfiles`` **doesn't**
support:

* Runs on Django 1.2.X.

* :attr:`~django.conf.settings.STATICFILES_EXCLUDED_APPS` settings -- A
  sequence of dotted app paths that should be ignored when searching for
  static files.

* :attr:`~django.conf.settings.STATICFILES_IGNORE_PATTERNS` settings -- A
  sequence of glob patterns of files and directories to ignore when running
  ``collectstatic``.

* Legacy 'media' dir file finder -- a staticfiles finder that supports the
  location for static files that a lot of 3rd party apps support
  (``staticfiles.finders.LegacyAppDirectoriesFinder``).

See the :doc:`settings` docs for more information.

Contents
--------

.. toctree::
   :maxdepth: 2

   commands
   helpers
   settings
   changelog
