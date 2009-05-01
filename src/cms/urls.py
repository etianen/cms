"""Base URLs for the CMS."""


from django.conf import settings
from django.conf.urls.defaults import *
from django.views.static import serve


urlpatterns = patterns("",)


# Set up CMS media serving.

if settings.CMS_MEDIA_URL.startswith("/"):
    cms_media_regex = r"^%s(.*)" % settings.CMS_MEDIA_URL.lstrip("/")
    urlpatterns += patterns("", url(cms_media_regex, serve, {"document_root": settings.CMS_MEDIA_ROOT}))


# Set up site-specific media serving.

if settings.SITE_MEDIA_URL.startswith("/"):
    site_media_regex = r"^%s(.*)" % settings.SITE_MEDIA_URL.lstrip("/")
    urlpatterns += patterns("", url(site_media_regex, serve, {"document_root": settings.SITE_MEDIA_ROOT}))
    
    