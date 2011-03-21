"""Views used by the CMS."""

from django.shortcuts import render


def handler500(request):
    """Renders a pretty error page."""
    response = render(request, "500.html", {})
    response.status_code = 500
    return response