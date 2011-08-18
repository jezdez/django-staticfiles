==================
django-staticfiles
==================

This is a Django app that provides helpers for serving static files.

Django developers mostly concern themselves with the dynamic parts of web
applications -- the views and templates that render new for each request. But
web applications have other parts: the static media files (images, CSS,
Javascript, etc.) that are needed to render a complete web page.

For small projects, this isn't a big deal, because you can just keep the media
somewhere your web server can find it. However, in bigger projects -- especially
those comprised of multiple apps -- dealing with the multiple sets of static
files provided by each application starts to get tricky.

That's what ``staticfiles`` is for:

    Collecting static files from each of your Django apps (and any other
    place you specify) into a single location that can easily be served in
    production.

The main website for django-staticfiles is
`github.com/jezdez/django-staticfiles`_ where you can also file tickets.

.. note:: django-staticfiles is now part of Django (since 1.3) as ``django.contrib.staticfiles``.

   The django-staticfiles 0.3.X series will only receive security and data los
   bug fixes after the release of django-staticfiles 1.0. Any Django 1.2.X
   project using django-staticfiles 0.3.X and lower should be upgraded to use
   either Django >= 1.3's staticfiles app or django-staticfiles >= 1.0 to
   profit from the new features and stability.

   You may want to chose to use django-staticfiles instead of Django's own
   staticfiles app since any new feature (additionally to those backported
   from Django) will be released first in django-staticfiles.

Installation
------------

- Use your favorite Python packaging tool to install ``staticfiles``
  from `PyPI`_, e.g.::

    pip install django-staticfiles

  You can also install the `in-development version`_ of django-staticfiles
  with ``pip install django-staticfiles==dev``.

- Added ``"staticfiles"`` to your ``INSTALLED_APPS`` setting::

    INSTALLED_APPS = [
        # ...
        "staticfiles",
    ]

- Set your ``STATIC_URL`` setting to the URL that handles serving
  static files::

    STATIC_URL = "/static/"

- In development mode (when ``DEBUG = True``) the ``runserver`` command will
  automatically serve static files::

    python manage.py runserver

- Once you are ready to deploy all static files of your site in a central
  directory (``STATIC_ROOT``) to be served by a real webserver (e.g. Apache_,
  Cherokee_, Lighttpd_, Nginx_ etc.), use the ``collectstatic`` management
  command::

    python manage.py collectstatic

  See the webserver's documentation for descriptions how to setup serving
  the deployment directory (``STATIC_ROOT``).

- (optional) In case you use Django's admin app, make sure the
  ``ADMIN_MEDIA_PREFIX`` setting is set correctly to a subpath of
  ``STATIC_URL``::

     ADMIN_MEDIA_PREFIX = STATIC_URL + "admin/"

.. _github.com/jezdez/django-staticfiles: http://github.com/jezdez/django-staticfiles
.. _in-development version: http://github.com/jezdez/django-staticfiles/tarball/develop#egg=django-staticfiles-dev
.. _PyPI: http://pypi.python.org/pypi/django-staticfiles
.. _Apache: http://httpd.apache.org/
.. _Lighttpd: http://www.lighttpd.net/
.. _Nginx: http://wiki.nginx.org/
.. _Cherokee: http://www.cherokee-project.com/
