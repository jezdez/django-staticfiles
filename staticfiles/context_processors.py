from staticfiles.settings import URL

def static_url(request):
    return {'STATIC_URL': URL}
