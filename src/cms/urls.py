"""Base URLs for the CMS."""


from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.contrib.syndication.views import feed
from django.views.static import serve

from cms.apps.feeds import registered_feeds
from cms.apps.pages.admin import site as admin_site
from cms.apps.pages.sitemaps import registered_sitemaps
from cms.apps.pages.models import publication_manager


admin.autodiscover()


urlpatterns = patterns("",
                       # TinyMCE configuration views.
                       url(r"^admin/tinymce-init.js$", "cms.apps.pages.views.tinymce_init", name="tinymce_init"),
                       url(r"^admin/tinymce-link-list.js$", "cms.apps.media.views.tinymce_link_list", name="tinymce_link_list"),
                       url(r"^admin/tinymce-image-list.js$", "cms.apps.media.views.tinymce_image_list", name="tinymce_image_list"),
                       # Page admin views.
                       url(r"^admin/reorder-pages/$", "cms.apps.pages.views.reorder_pages", name="reorder_pages"),
                       # Admin views.
                       url(r"^admin/", include(admin_site.urls)),
                       # Permalink redirection service.
                       url(r"^links/(?P<content_type_id>\d+)/(?P<object_id>.+)/$", "cms.apps.pages.views.permalink_redirect", name="permalink_redirect"),
                       # Google sitemap service.
                       url(r"^sitemap.xml$", publication_manager.published_view(sitemap), {"sitemaps": registered_sitemaps}, name="sitemap"),
                       # RSS feed service.
                       url(r"^feeds/(?P<url>.*)/$", publication_manager.published_view(feed), {"feed_dict": registered_feeds}, name="feeds"),
                       # Basic robots.txt.
                       url(r"^robots.txt$", "django.views.generic.simple.direct_to_template", kwargs={"template": "robots.txt", "mimetype": "text/plain"}),)


# Template preview service, only in DEBUG and TEMPLATE_DEBUG.

if settings.DEBUG and settings.TEMPLATE_DEBUG:
    urlpatterns += patterns("", url(r"^templates/(.*)", "cms.apps.pages.views.render_template"))


# Set up static media serving.

if settings.SERVE_STATIC_MEDIA:
    for media_url, media_root in settings.STATIC_MEDIA:
        media_regex = r"^%s(.*)" % media_url.lstrip("/")
        urlpatterns += patterns("", url(media_regex, serve, {"document_root": media_root}))


handler404 = "cms.apps.pages.views.handler404"


handler500 = "cms.apps.pages.views.handler500"

