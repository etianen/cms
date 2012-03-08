"""URLs used by the CMS admin extensions."""

from functools import wraps

from django.conf.urls import patterns, url

from cms.admin import views


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
        url(r"^$", patched_admin_view(views.index), name="index"),
        url(r"^tinymce-init.js$", admin_view(patched_admin_view(views.tinymce_init)), name="tinymce_init"),
        url(r"^tinymce-link-list.js$", admin_view(patched_admin_view(views.tinymce_link_list)), name="tinymce_link_list"),
        url(r"^sitemap.json$", admin_view(patched_admin_view(views.sitemap_json)), name="sitemap_json"),
        url(r"^move-page/$", admin_view(patched_admin_view(views.move_page)), name="move_page"),
    ) + admin_site.get_urls()
    # Patch all the views to disable publication management.
    print urls
    
    return urls