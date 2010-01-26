"""URLs used by the search application."""


from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("cms.apps.search.views",
                       url(r"^$", "index", name="index"))

