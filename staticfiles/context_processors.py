import warnings
from django.conf import settings

def static(request):
    """
    Adds static-related context variables to the context.
    """
    return {'STATIC_URL': settings.STATIC_URL}

def static_url(request):
    warnings.warn(
        "The context processor 'staticfiles.context_processors.static_url' "
        "was renamed to 'staticfiles.context_processors.static'.",
        DeprecationWarning)
    return static(request)
