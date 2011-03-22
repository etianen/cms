"""Context processors used by the pages application."""

from cms.apps.pages.models import Page


def page(request):
    """Places the current page in the template."""
    page = request.page
    homepage = Page.objects.get_homepage()
    context = {
        "page": page,
        "homepage": homepage,
        "is_homepage": homepage.get_absolute_url() == request.path,
    }
    return context
    
    