"""Views used by the CMS."""


from django.template import RequestContext
from django.shortcuts import render_to_response


def handler500(request):
    """Renders a pretty error page."""
    response = render_to_response("500.html", {}, RequestContext(request))
    response.status_code = 500
    return response