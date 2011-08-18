=======
Helpers
=======

.. module:: staticfiles
   :synopsis: An app for handling static files.

Context processors
==================

The ``static`` context processor
--------------------------------

.. function:: context_processors.static

This context processor adds the ``STATIC_URL`` into each template
context as the variable ``{{ STATIC_URL }}``. To use it, make sure that
``'staticfiles.context_processors.static'`` appears somewhere in your
``TEMPLATE_CONTEXT_PROCESSORS`` setting.

Remember, only templates rendered with a ``RequestContext`` will have
acces to the data provided by this (and any) context processor.

Template tags
=============

.. highlight:: html+django

static
------

.. function:: templatetags.staticfiles.static

.. versionadded:: 1.1

Uses the configued :ref:`STATICFILES_STORAGE` storage to create the
full URL for the given relative path, e.g.::

    {% load staticfiles %}
    <img src="{% static "css/base.css" %}" />

The previous example is equal to calling the ``url`` method of an instance of
:ref:`STATICFILES_STORAGE` with ``"css/base.css"``. This is especially
useful when using a non-local storage backend to `deploy files to a CDN`_.

.. _`deploy files to a CDN`: https://docs.djangoproject.com/en/dev/howto/static-files/#serving-static-files-from-a-cloud-service-or-cdn

get_static_prefix
-----------------

.. function:: templatetags.static.get_static_prefix

If you're not using ``RequestContext``, or if you need more control over
exactly where and how ``STATIC_URL`` is injected into the template,
you can use the ``get_static_prefix`` template tag instead::

   {% load static %}
   <img src="{% get_static_prefix %}images/hi.jpg" />

There's also a second form you can use to avoid extra processing if you need
the value multiple times::

   {% load static %}
   {% get_static_prefix as STATIC_PREFIX %}

   <img src="{{ STATIC_PREFIX }}images/hi.jpg" />
   <img src="{{ STATIC_PREFIX }}images/hi2.jpg" />

get_media_prefix
----------------

.. function:: templatetags.static.get_media_prefix

Similar to :func:`~staticfiles.templatetags.static.get_static_prefix` but
uses the ``MEDIA_URL`` setting instead.

Storages
========

StaticFilesStorage
------------------

.. class:: storage.StaticFilesStorage

   A subclass of the :class:`~django.core.files.storage.FileSystemStorage`
   storage backend that uses the :ref:`STATIC_ROOT` setting as the base
   file system location and the :ref:`STATIC_URL` setting respectively
   as the base URL.

   .. method:: post_process(paths, **options)

   .. versionadded:: 1.1

   This method is called by the :ref:`collectstatic` management command
   after each run and gets passed the paths of found files, as well as the
   command line options.

   The :class:`~staticfiles.storage.CachedStaticFilesStorage` uses this
   behind the scenes to replace the paths with their hashed counterparts
   and update the cache appropriately.

CachedStaticFilesStorage
------------------------

.. class:: storage.CachedStaticFilesStorage

   .. versionadded:: 1.1

   A subclass of the :class:`~staticfiles.storage.StaticFilesStorage`
   storage backend which caches the files it saves by appending the MD5 hash
   of the file's content to the filename. For example, the file
   ``css/styles.css`` would also be saved as ``css/styles.55e7cbb9ba48.css``.

   The purpose of this storage is to keep serving the old files in case some
   pages still refer to those files, e.g. because they are cached by you or
   a 3rd party proxy server. Additionally, it's very helpful if you want to
   apply `far future Expires headers`_ to the deployed files to speed up the
   load time for subsequent page visits.

   The storage backend automatically replaces the paths found in the saved
   files matching other saved files with the path of the cached copy (using
   the :meth:`~staticfiles.storage.StaticFilesStorage.post_process`
   method). The regular expressions used to find those paths
   (``storage.CachedStaticFilesStorage.cached_patterns``)
   by default cover the `@import`_ rule and `url()`_ statement of `Cascading
   Style Sheets`_. For example, the ``'css/styles.css'`` file with the
   content

   .. code-block:: css+django

       @import url("../admin/css/base.css");

   would be replaced by calling the
   :meth:`~django.core.files.storage.Storage.url`
   method of the ``CachedStaticFilesStorage`` storage backend, ultimatively
   saving a ``'css/styles.55e7cbb9ba48.css'`` file with the following
   content:

   .. code-block:: css+django

       @import url("/static/admin/css/base.27e20196a850.css");

   To enable the ``CachedStaticFilesStorage`` you have to make sure the
   following requirements are met:

   * the :ref:`STATICFILES_STORAGE` setting is set to
     ``'staticfiles.storage.CachedStaticFilesStorage'``
   * the ``DEBUG`` setting is set to ``False``
   * you use the ``staticfiles``
     :func:`~staticfiles.templatetags.static.static` template
     tag to refer to your static files in your templates
   * you've collected all your static files by using the
     :ref:`collectstatic` management command

   Since creating the MD5 hash can be a performance burden to your website
   during runtime, ``staticfiles`` will automatically try to cache the
   hashed name for each file path using Django's caching framework. If you
   want to override certain options of the cache backend the storage uses,
   simply specify a custom entry in the ``CACHES`` setting named
   ``'staticfiles'``. It falls back to using the ``'default'`` cache backend.

.. _`far future Expires headers`: http://developer.yahoo.com/performance/rules.html#expires
.. _`@import`: http://www.w3.org/TR/CSS2/cascade.html#at-import
.. _`url()`: http://www.w3.org/TR/CSS2/syndata.html#uri
.. _`Cascading Style Sheets`: http://www.w3.org/Style/CSS/


.. _staticfiles-development-view:

Static file development view
----------------------------

.. highlight:: python

.. function:: staticfiles.views.serve(request, path)

This view function serves static files in development.

.. warning::

   This view will only work if ``DEBUG`` is ``True``.

   That's because this view is **grossly inefficient** and probably
   **insecure**. This is only intended for local development, and should
   **never be used in production**.

This view is automatically enabled by ``runserver`` (with a
``DEBUG`` setting set to ``True``). To use the view with a different
local development server, add the following snippet to the end of your
primary URL configuration::

  from django.conf import settings

  if settings.DEBUG:
      urlpatterns += patterns('staticfiles.views',
          url(r'^static/(?P<path>.*)$', 'serve'),
      )

Note, the begin of the pattern (``r'^static/'``) should be your
``STATIC_URL`` setting.

URL patterns helper
-------------------

.. function:: staticfiles.urls.staticfiles_urlpatterns()

.. warning::

   This helper function will only work if ``DEBUG`` is ``True``
   and your ``STATIC_URL`` setting is neither empty nor a full
   URL such as ``http://static.example.com/``.

Since configuring the URL patterns is a bit finicky, there's also a helper
function that'll do this for you.

This will return the proper URL pattern for serving static files to your
already defined pattern list. Use it like this::

  from staticfiles.urls import staticfiles_urlpatterns

  # ... the rest of your URLconf here ...

  urlpatterns += staticfiles_urlpatterns()
