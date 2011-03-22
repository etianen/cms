"""Context processors used by the pages application."""

from cms.apps.pages.models import Page


def homepage(request):
    """Places the current page in the template."""
    homepage = Page.objects.get_homepage()
    context = {
        "homepage": homepage,
        "is_homepage": homepage.get_absolute_url() == request.path,
    }
    return context
    
    