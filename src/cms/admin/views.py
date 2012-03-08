"""Views used by the CMS admin extensions."""

from functools import wraps

from django.shortcuts import render

from cms.models.managers import publication_manager


# The GET parameter used to indicate where page admin actions originated.
PAGE_FROM_KEY = "from"

# The GET parameter value used to indicate that the page admin action came form the sitemap.
PAGE_FROM_SITEMAP_VALUE = "sitemap"


def admin_view(view, *args, **kwargs):
    """Turns off publication management for admin views."""
    @wraps(view)
    def do_admin_view(*args, **kwargs):
        with publication_manager.select_published(False):
            return view(*args, **kwargs)
    return do_admin_view


def tinymce_init(admin_site, request):
    """Renders the tinymce init script."""
    return render(request, "admin/tinymce_init.js", {}, content_type="text/javascript; charset=utf-8")