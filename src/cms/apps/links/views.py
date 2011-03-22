"""Views used by the links application."""


from django.shortcuts import redirect

from cms.apps.pages.models import Page


def index(request, page):
    """Redirects to a new page."""
    link_url = page.content.link_url
    return redirect(link_url)

