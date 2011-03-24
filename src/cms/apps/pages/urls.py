"""URLs used by the standard content page."""

from django.conf.urls.defaults import patterns, url

from cms.apps.pages import views


urlpatterns = patterns("cms.apps.pages.views",

    url(r"^$", views.ContentIndexView.as_view(), name="index")
    
)