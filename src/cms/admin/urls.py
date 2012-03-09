"""URLs used by the CMS admin extensions."""

from django.core.urlresolvers import RegexURLPattern, RegexURLResolver

from cms.admin import views


def decorate(decorator, urlconf):
    """Decorates a urlconf with a singe decorator."""
    if isinstance(urlconf, (list, tuple)):
        for item in urlconf:
            decorate(decorator, item)
    elif isinstance(urlconf, RegexURLResolver):
        for item in urlconf.url_patterns:
            decorate(decorator, item)
    elif isinstance(urlconf, RegexURLPattern):
        urlconf._callback = decorator(urlconf.callback)
    return urlconf


def get_urls(admin_site):
    """Generates the patched CMS admin urls."""
    # Add the addional views to the listing.
    urls = admin_site.get_urls()
    # Patch all the views to disable publication management.
    urls = decorate(views.admin_view, urls)
    return urls