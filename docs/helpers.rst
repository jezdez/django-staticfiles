Helpers
=======

The ``static`` context processor
--------------------------------

.. function:: staticfiles.context_processors.static

This context processor adds the ``STATIC_URL`` into each template
context as the variable ``{{ STATIC_URL }}``. To use it, make sure that
``'staticfiles.context_processors.static'`` appears somewhere in your
``TEMPLATE_CONTEXT_PROCESSORS`` setting.

Remember, only templates rendered with a ``RequestContext`` will have
acces to the data provided by this (and any) context processor.

The ``get_static_prefix`` templatetag
-------------------------------------

.. highlight:: html+django

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
