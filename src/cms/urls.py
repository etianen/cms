"""Base URLs for the CMS."""

from django.conf import settings
from django.conf.urls.defaults import patterns, url, include, handler404  # pyline: disable=W0611
from django.contrib import admin
from django.views import generic

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
    url(r"^robots.txt$", "django.views.generic.simple.direct_to_template", kwargs={"template": "robots.txt", "mimetype": "text/plain"}, name="robots_txt"),
    
    # Redirect to a sensible favicon location. At the very least, this will keep the 404 page out of Django, saving database hits.
    url(r"favicon.ico$", generic.RedirectView.as_view(
        url = settings.STATIC_URL + "site/img/favicon.png",
    ), name="favicon.ico"),
    
)


if settings.DEBUG:
    urlpatterns += patterns("",
        url("^{0}(.+)".format(settings.MEDIA_URL[1:]), "django.views.static.serve", kwargs={"document_root": settings.MEDIA_ROOT})
    )


handler500 = "cms.core.views.handler500"