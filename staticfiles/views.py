"""
Views and functions for serving static files. These are only to be used during
development, and SHOULD NOT be used in a production setting.

"""
import os
from django import http
from django.views.static import serve as django_serve
from staticfiles.resolvers import resolve


def serve(request, path, show_indexes=False):
    """
    Serve static files from locations inferred from INSTALLED_APPS and
    STATICFILES_DIRS.

    To use, put a URL pattern such as::

        (r'^(?P<path>.*)$', 'staticfiles.views.serve')

    in your URLconf. You may also set ``show_indexes`` to ``True`` if you'd
    like to serve a basic index of the directory.  This index view will use the
    template hardcoded below, but if you'd like to override it, you can create
    a template called ``static/directory_index``.
    
    """
    absolute_path = resolve(path)
    if not absolute_path:
        raise http.Http404('%r could not be resolved to a static file.' % path)
    absolute_path, filename = os.path.split(absolute_path)
    return django_serve(request, path=filename, document_root=absolute_path,
                        show_indexes=show_indexes)
