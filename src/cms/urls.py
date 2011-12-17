"""Base URLs for the CMS."""

from django.conf import settings
from django.conf.urls.defaults import patterns, url, include, handler404
from django.contrib import admin
from django.views import generic
from django.conf.urls.static import static

from cms.admin import site as admin_site
from cms.sitemaps import registered_sitemaps
from cms.views import TextTemplateView


admin.autodiscover()


urlpatterns = patterns("",

    # Admin views.
    url(r"^admin/", include(admin_site.urls)),
    
    # Permalink redirection service.
    url(r"^r/(?P<content_type_id>\d+)-(?P<object_id>[^/]+)/$", "django.contrib.contenttypes.views.shortcut", name="permalink_redirect"),
    
    # Google sitemap service.
    url(r"^sitemap.xml$", "django.contrib.sitemaps.views.index", {"sitemaps": registered_sitemaps}),
    url(r"^sitemap-(?P<section>.+)\.xml$", "django.contrib.sitemaps.views.sitemap", {"sitemaps": registered_sitemaps}),
    
    # Basic robots.txt.
    url(r"^robots.txt$", TextTemplateView.as_view(template_name="robots.txt")),
    
    # There's no favicon here!
    url(r"^favicon.ico$", generic.RedirectView.as_view()),
    
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += patterns("",
        url("^404/$", generic.TemplateView.as_view(template_name="404.html")),
        url("^500/$", generic.TemplateView.as_view(template_name="500.html")),
    )


handler500 = "cms.views.handler500"


handler404 = handler404