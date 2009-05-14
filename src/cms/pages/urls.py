"""URLs used by the page management application."""


from django.conf.urls.defaults import *


urlpatterns = patterns("cms.pages.views",
                       url(r"^(.*/)$", "dispatch", name="page"),
                       url(r"^$", "dispatch", name="homepage"),)

