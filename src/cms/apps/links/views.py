"""Views used by the links application."""

from django.shortcuts import redirect


def index(request):
    """Redirects to a new page."""
    return redirect(request.pages.current.content.get_link_url_resolved())