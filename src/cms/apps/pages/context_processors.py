"""Context processors used by the pages application."""


def pages(request):
    """Adds the current page backend to the template."""
    context = {
        "pages": request.pages,
    }
    return context