"""URLs used by the standard content page."""

from django.conf.urls.defaults import patterns, url
from django.views.generic import TemplateView


urlpatterns = patterns("",

    url(r"^$", TemplateView.as_view(
        template_name = "pages/base.html"
    ), name="index")
    
)