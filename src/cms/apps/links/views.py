"""Views used by the links application."""


from django.shortcuts import redirect

from cms.apps.pages.models import Page


def index(request):
    """Redirects to a new page."""
    redirect_url = request.page.content.redirect_url
    redirect_url = Page.objects.expand_page_url(redirect_url)
    return redirect(redirect_url)

