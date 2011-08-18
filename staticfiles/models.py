# Initialize the settings.
from staticfiles import settings

# Okay, this is ugly, but I don't see another way except adding a registry
# pattern thingie to Django which seems like overengineering. Meh.
try:
    from django.contrib.admin.templatetags import admin_static
except ImportError:
    # We leave Django alone since there isn't a admin_static module.
    pass
else:
    # Heck, we patch the hell out of it, err, replace the default static tag.
    from staticfiles.templatetags.staticfiles import static
    admin_static.static = admin_static.register.simple_tag(static)
