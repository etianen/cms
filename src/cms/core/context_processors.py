"""Context processors used by the CMS."""


from django.conf import settings
from django.contrib.sites.models import Site


def site(request):
    """Sets the site name and domain in the template."""
    context = {"site": Site.objects.get_current()}
    return context


def conf(request):
    """Gives the settings object to the template."""
    context = {
        "settings": settings
    }
    return context
    
    
def pages(request):
    """Adds the current page backend to the template."""
    context = {
        "pages": request.pages
    }
    return context