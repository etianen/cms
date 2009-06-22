"""URLs used by the page management application."""


from django.conf.urls.defaults import *


urlpatterns = patterns("cms.apps.pages.views",
                       url(r"^.*/$", "render_page", name="render_page"),
                       url(r"^$", "render_page", name="render_homepage"),)

