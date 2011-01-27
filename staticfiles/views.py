"""
Views and functions for serving static files. These are only to be used during
development, and SHOULD NOT be used in a production setting.

"""
import os
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.http import Http404

try:
    from django.contrib.staticfiles.views import serve as django_serve
except ImportError:
    from django.views.static import serve as django_serve

from staticfiles import finders

def serve(request, path, show_indexes=False, insecure=False):
    """
    Serve static files below a given point in the directory structure or
    from locations inferred from the static files finders.

    To use, put a URL pattern such as::

        (r'^(?P<path>.*)$', 'staticfiles.views.serve')

    in your URLconf.

    If you provide the ``document_root`` parameter, the file won't be looked
    up with the staticfiles finders, but in the given filesystem path, e.g.::

    (r'^(?P<path>.*)$', 'staticfiles.views.serve', {'document_root' : '/path/to/my/files/'})

    You may also set ``show_indexes`` to ``True`` if you'd like to serve a
    basic index of the directory.  This index view will use the
    template hardcoded below, but if you'd like to override it, you can create
    a template called ``static/directory_index.html``.
    """
    if not settings.DEBUG and not insecure:
        raise ImproperlyConfigured("The view to serve static files can only "
                                   "be used if the DEBUG setting is True or "
                                   "the --insecure option of 'runserver' is "
                                   "used")
    absolute_path = finders.find(path)
    if not absolute_path:
        raise Http404('"%s" could not be found' % path)
    document_root, path = os.path.split(absolute_path)
    return django_serve(request, path=path, document_root=document_root,
                        show_indexes=show_indexes)
