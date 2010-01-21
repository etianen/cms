"""Base URLs for the CMS."""


from django.conf import settings
from django.conf.urls.defaults import patterns, url, include, handler404  # @UnusedImport
from django.contrib import admin
from django.views.static import serve

from cms.apps.pages.admin import site as admin_site
from cms.apps.pages.sitemaps import registered_sitemaps


__all__ = ("patterns", "url", "include", "urlpatterns", "handler404", "handler500",)


admin.autodiscover()


urlpatterns = patterns("",
                       # Admin views.
                       url(r"^admin/", include(admin_site.urls)),
                       # Permalink redirection service.
                       url(r"^links/(?P<content_type_id>\d+)/(?P<object_id>.+)/$", "django.contrib.contenttypes.views.shortcut", name="permalink_redirect"),
                       # Google sitemap service.
                       url(r"^sitemap.xml$", "django.contrib.sitemaps.views.index", {"sitemaps": registered_sitemaps}, name="sitemap"),
                       url(r"^sitemap-(?P<section>.+)\.xml$", "django.contrib.sitemaps.views.sitemap", {"sitemaps": registered_sitemaps}),
                       # Basic robots.txt.
                       url(r"^robots.txt$", "django.views.generic.simple.direct_to_template", kwargs={"template": "robots.txt", "mimetype": "text/plain"}, name="robots_txt"),)


# Set up static media serving.

if settings.SERVE_STATIC_MEDIA:
    for media_url, media_root in settings.STATIC_MEDIA:
        media_regex = r"^%s(.*)" % media_url.lstrip("/")
        urlpatterns += patterns("", url(media_regex, serve, {"document_root": media_root}))


handler500 = "cms.apps.pages.views.handler500"

