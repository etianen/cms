"""Base views used by page models."""


from django.shortcuts import render


def index(request):
    """Renders the default index page for page content."""
    page = request.page
    template_name = ("pages/%s.html" % page.content.__class__.__name__.lower(),
                     "pages/base.html")
    return render(request, template_name, {})