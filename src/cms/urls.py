"""Base URLs for the CMS."""


from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin
from django.views.static import serve

from cms.apps.pages.admin import site as admin_site


admin.autodiscover()


urlpatterns = patterns("",
                       url(r"^admin/(.*)", admin_site.root),
                       # Permalink redirection service.
                       url(r"^links/(\d+)/(.+)/$", "cms.apps.pages.views.permalink_redirect", name="permalink_redirect"),
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

urlpatterns += patterns("", url(r"^", include("cms.apps.pages.urls")),)

