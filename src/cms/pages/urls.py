"""URLs used by the page management application."""


from django.conf.urls.defaults import *


urlpatterns = patterns("cms.pages.views",
                       url(r"^(.*/)$", "page", name="page"),
                       url(r"^$", "page", name="homepage"),)

