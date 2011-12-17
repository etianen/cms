"""Context processors used by the CMS."""

from django.conf import settings as django_settings


def settings(request):
    """Gives the settings object to the template."""
    context = {
        "settings": django_settings
    }
    return context
    
    
def pages(request):
    """Adds the current page backend to the template."""
    context = {
        "pages": request.pages,
    }
    return context