Helpers
=======

``static_url`` context processor
--------------------------------

To refer to static file assets from a template, ensure you have set the
:ref:`static-url` setting to the URL path where the static files are served.

Next, add the ``static_url`` context processor to your
``TEMPLATE_CONTEXT_PROCESSORS`` setting::

   TEMPLATE_CONTEXT_PROCESSORS = (
       'staticfiles.context_processors.static_url',
   )

Templates rendered with ``RequestContext`` will now have access to a
:ref:`static-url` context variable::

   <link href="{{ STATIC_URL }}css/polls.css" rel="stylesheet" type="text/css" />


Serving static files during development
---------------------------------------

.. warning:: Don't use this on production servers.
  This feature is **only intended for development**.
  Please, don't shoot yourself in the foot. Thanks.

To serve static media for both ``MEDIA_URL`` and :ref:`static-url` add the
following snippet to the end of your primary URL configuration::

   from django.conf import settings
   from staticfiles.urls import staticfiles_urlpatterns

   if settings.DEBUG:
       urlpatterns += staticfiles_urlpatterns()
