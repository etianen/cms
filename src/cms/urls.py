"""Base URLs for the CMS."""


from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.static import serve

from cms.apps.pages.admin import site as admin_site
from cms.apps.pages.views import handler500


admin.autodiscover()


urlpatterns = patterns("",
                       # TinyMCE configuration views.
                       url(r"^admin/tinymce-init.js$", "cms.apps.pages.views.tinymce_init", name="tinymce_init"),
                       url(r"^admin/tinymce-link-list.js$", "cms.apps.media.views.tinymce_link_list", name="tinymce_link_list"),
                       url(r"^admin/tinymce-image-list.js$", "cms.apps.media.views.tinymce_image_list", name="tinymce_image_list"),
                       # Page admin views.
                       url(r"^admin/reorder-pages/$", "cms.apps.pages.views.reorder_pages", name="reorder_pages"),
                       # Admin views.
                       url(r"^admin/(.*)", admin_site.root),
                       # Permalink redirection service.
                       url(r"^links/(?P<content_type_id>\d+)/(?P<object_id>.+)/$", "cms.apps.pages.views.permalink_redirect", name="permalink_redirect"),
                       url(r"^robots.txt$", "django.views.generic.simple.direct_to_template", kwargs={"template": "robots.txt", "mimetype": "text/plain"}),)


# Template preview service, only in DEBUG and TEMPLATE_DEBUG.

if settings.DEBUG and settings.TEMPLATE_DEBUG:
    urlpatterns += patterns("", url(r"^templates/(.*)", "cms.apps.pages.views.render_template"))


# Set up static media serving.

if settings.SERVE_STATIC_MEDIA:
    for media_url, media_root in settings.STATIC_MEDIA:
        media_regex = r"^%s(.*)" % media_url.lstrip("/")
        urlpatterns += patterns("", url(media_regex, serve, {"document_root": media_root}))


# Final pattern is the catch-all for page serving.

urlpatterns += patterns("cms.apps.pages.views",
                        url(r"^(.*)$", "render_page", name="render_page"),
                        url(r"^$", "render_page", name="render_homepage"),)

