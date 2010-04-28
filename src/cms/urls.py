"""Base URLs for the CMS."""


from django.conf import settings
from django.conf.urls.defaults import patterns, url, include, handler404  # @UnusedImport
from django.contrib import admin

from cms.core.admin import site as admin_site
from cms.core.sitemaps import registered_sitemaps


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

if settings.MEDIA_DEBUG:
    def media_url(media_url, media_root):
        return url(r"^%s(.*)" % media_url.lstrip("/"), "serve", {"document_root": media_root})
    urlpatterns += patterns("django.views.static",
                            media_url(settings.CMS_MEDIA_URL, settings.CMS_MEDIA_ROOT),
                            media_url(settings.SITE_MEDIA_URL, settings.SITE_MEDIA_ROOT),
                            media_url(settings.MEDIA_URL, settings.MEDIA_ROOT),)


handler500 = "cms.apps.pages.views.handler500"