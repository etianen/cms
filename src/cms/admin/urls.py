"""URLs used by the CMS admin extensions."""

from functools import wraps

from django.conf.urls import patterns, url
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
    admin_view = admin_site.admin_view
    def patched_admin_view(func):
        @wraps(func)
        def do_patched_admin_view(request, *args, **kwargs):
            return func(admin_site, request, *args, **kwargs)
        return do_patched_admin_view
    # Add the addional views to the listing.
    urls = patterns("",
        url(r"^tinymce-init.js$", admin_view(patched_admin_view(views.tinymce_init)), name="tinymce_init"),
    ) + admin_site.get_urls()
    # Patch all the views to disable publication management.
    urls = decorate(views.admin_view, urls)
    return urls