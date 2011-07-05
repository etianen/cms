"""Views used by the links application."""

from django.shortcuts import redirect

from cms.apps.pages.models import Page


def index(request):
    """Redirects to a new page."""
    link_url = request.pages.current.content.link_url
    # Process the link.
    if link_url.lower().startswith("page://"):
        try:
            page = request.pages.get(link_url[7:])
        except Page.DoesNotExist:
            link_url = request.pages.homepage.get_absolute_url()
        else:
            link_url = page.get_absolute_url()
    # Redirect to link.
    return redirect(link_url)

