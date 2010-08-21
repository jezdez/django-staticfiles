==================
django-staticfiles
==================

This is a Django app that provides helpers for serving static files.

The main website for django-staticfiles is
`bitbucket.org/jezdez/django-staticfiles`_ where you can also file tickets.

You can also install the `in-development version`_ of django-staticfiles with
``pip install django-staticfiles==dev`` or ``easy_install django-staticfiles==dev``.

.. note:: When using ``django-staticfiles`` with your own apps, make sure
   they can be found by Django's app loading mechanism. Simply include
   a ``models`` module (an empty ``models.py`` file suffices) and add the
   app to the ``INSTALLED_APPS`` setting of your site.

.. _bitbucket.org/jezdez/django-staticfiles: http://bitbucket.org/jezdez/django-staticfiles/
.. _in-development version: http://bitbucket.org/jezdez/django-staticfiles/get/tip.gz#egg=django-staticfiles-dev
