"""Views used by the links application."""

from django.shortcuts import redirect


def index(request):
    """Redirects to a new page."""
    link_url = request.pages.current.content.link_url
    return redirect(link_url)

