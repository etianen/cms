"""Core views used by the CMS."""


from django import template
from django.shortcuts import render_to_response


def index(request):
    """Renders the default index page for page content."""
    page = request.page
    template_name = ("pages/%s.html" % page.content.__class__.__name__.lower(),
                     "pages/base.html")
    return page.render_to_response(request, template_name)


def handler500(request):
    """Renders a pretty error page."""
    response = render_to_response("500.html", {}, template.RequestContext(request))
    response.status_code = 500
    return response

