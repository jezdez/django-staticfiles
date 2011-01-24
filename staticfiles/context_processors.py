from django.conf import settings

def static_url(request):
    """
    Adds static-related context variables to the context.

    """
    return {'STATIC_URL': settings.STATIC_URL}

