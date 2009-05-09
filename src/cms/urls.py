"""Base URLs for the CMS."""


from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.static import serve


admin.autodiscover()


urlpatterns = patterns("",
                       (r'^admin/', include(admin.site.urls)),)


# Set up static media serving.

if settings.SERVE_STATIC_MEDIA:
    for media_url, media_root in settings.STATIC_MEDIA:
        media_regex = r"^%s(.*)" % media_url.lstrip("/")
        urlpatterns += patterns("", url(media_regex, serve, {"document_root": media_root}))

