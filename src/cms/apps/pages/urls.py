"""URLs used by the standard content page."""


from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("cms.apps.pages.views",
                       url(r"^$", "index", name="index"))

