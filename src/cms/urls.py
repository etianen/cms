"""Base URLs for the CMS."""


from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.static import serve

from cms.core.admin import site as admin_site


admin.autodiscover()


urlpatterns = patterns("",
                       url(r"^admin/", include(admin_site.urls)),
                       url(r"^links/(\d+)/(.+)/$", "cms.core.views.permalink_redirect", name="permalink_redirect"),
                       url(r"^", include("cms.pages.urls")),)


# Set up static media serving.

if settings.SERVE_STATIC_MEDIA:
    for media_url, media_root in settings.STATIC_MEDIA:
        media_regex = r"^%s(.*)" % media_url.lstrip("/")
        urlpatterns += patterns("", url(media_regex, serve, {"document_root": media_root}))

