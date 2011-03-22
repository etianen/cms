"""URLs used by the standard content page."""

from django.conf.urls.defaults import patterns, url

from cms.apps.pages.views import CurrentPageView


urlpatterns = patterns("",

    url(r"^$", CurrentPageView.as_view(), name="index")
    
)