==================
django-staticfiles
==================

This is a Django app that provides helpers for serving static files.

Django developers mostly concern themselves with the dynamic parts of web
applications -- the views and templates that render anew for each request. But
web applications have other parts: the static media files (images, CSS,
Javascript, etc.) that are needed to render a complete web page.

For small projects, this isn't a big deal, because you can just keep the media
somewhere your web server can find it. However, in bigger projects -- especially
those comprised of multiple apps -- dealing with the multiple sets of static
files provided by each application starts to get tricky.

That's what ``staticfiles`` is for: it collects media from each of your
applications (and any other places you specify) into a single location
that can easily be served in production.

The main website for django-staticfiles is
`github.com/jezdez/django-staticfiles`_ where you can also file tickets.

.. warning:: django-staticfiles was added to Django 1.3 as a contrib app.
   For backwards compatible reasons, django-staticfiles 0.3.X series will be
   the last series to only support Django 1.2.X and lower. Any new features
   (including those backported from Django) will occur in later releases,
   e.g. in django-staticfiles>=1.0.X.

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

.. _github.com/jezdez/django-staticfiles: http://github.com/jezdez/django-staticfiles
.. _in-development version: http://github.com/jezdez/django-staticfiles/tarball/develop#egg=django-staticfiles-dev
.. _PyPI: http://pypi.python.org/pypi/django-staticfiles
.. _Apache: http://httpd.apache.org/
.. _Lighttpd: http://www.lighttpd.net/
.. _Nginx: http://wiki.nginx.org/
.. _Cherokee: http://www.cherokee-project.com/
