Changelog
=========

v0.3.0 (2010-08-18)
-------------------

* Added resolver API which abstract the way staticfiles finds files.

* Added staticfiles.urls.staticfiles_urlpatterns to avoid the catch-all
  URLpattern which can make top-level urls.py slightly more confusing.
  From Brian Rosner.

* Minor documentation changes

* Updated testrunner to work with Django 1.1.X and 1.2.X.

* Removed custom code to load storage backend.

v0.2.0 (2009-11-25)
-------------------

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

v0.1.2 (2009-09-02)
-------------------

* Fixed a typo in settings.py

* Fixed a conflict in build_media (now build_static) between handling
  non-namespaced app media and other files with the same relative path.

v0.1.1 (2009-09-02)
-------------------

* Added README with a bit of documentation :)

v0.1.0 (2009-09-02)
-------------------

* Initial checkin from Pinax' source.

* Will create the STATIC_ROOT directory if not existent.
