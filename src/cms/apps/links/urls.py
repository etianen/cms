"""URLs used by the links application."""


from django.conf.urls import url, patterns


urlpatterns = patterns("cms.apps.links.views",
                       url(r"^$", "index", name="index"))