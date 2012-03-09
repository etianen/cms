"""URLs used by the standard content page."""

from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_protect

from cms.apps.pages import views


urlpatterns = patterns("cms.apps.pages.views",

    url(r"^$", csrf_protect(views.ContentIndexView.as_view()), name="index")
    
)