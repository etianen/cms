"""Base views used by page models."""


from django.shortcuts import render_to_response
from django.template import RequestContext


def index(request):
    """Renders the default index page for page content."""
    page = request.page
    template_name = ("pages/%s.html" % page.content.__class__.__name__.lower(),
                     "pages/base.html")
    return render_to_response(template_name, {}, RequestContext(request))