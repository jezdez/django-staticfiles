Helpers
=======

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
