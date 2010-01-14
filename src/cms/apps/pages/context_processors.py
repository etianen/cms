"""Context processors used by the CMS."""


from django.conf import settings
from django.contrib.sites.models import Site

from cms.apps.pages.models import Page


def site(request):
    """Sets the site name and domain in the template."""
    context = {"site": Site.objects.get_current()}
    return context


def media(request):
    """Sets up the site and cms media references in the template."""
    context = {"SITE_MEDIA_URL": settings.SITE_MEDIA_URL,
               "CMS_MEDIA_URL": settings.CMS_MEDIA_URL}
    return context


def conf(request):
    """Gives the settings object to the template."""
    context = {"settings": settings}
    return context


def page(request):
    """Places the current page in the template."""
    context = {"page": request.page}
    return context
    
    