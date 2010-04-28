"""Base views used by page models."""


def index(request):
    """Renders the default index page for page content."""
    page = request.page
    template_name = ("pages/%s.html" % page.content.__class__.__name__.lower(),
                     "pages/base.html")
    return page.render_to_response(request, template_name)