"""Base URLs for the CMS."""


from django.conf import settings
from django.conf.urls.defaults import patterns, url, include, handler404  # @UnusedImport
from django.contrib import admin

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

if settings.MEDIA_DEBUG:
    def media_regex(media_url):
        return r"^%s(.*)" % media_url.lstrip("/")
    urlpatterns += patterns("django.views.static",
                            url(media_regex(settings.CMS_MEDIA_URL), "serve", {"document_root": settings.CMS_MEDIA_ROOT}),
                            url(media_regex(settings.SITE_MEDIA_URL), "serve", {"document_root": settings.SITE_MEDIA_ROOT}),
                            url(media_regex(settings.MEDIA_URL), "serve", {"document_root": settings.MEDIA_ROOT}))


handler500 = "cms.apps.pages.views.handler500"