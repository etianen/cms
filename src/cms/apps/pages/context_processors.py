"""Context processors used by the pages application."""


def page(request):
    """Places the current page in the template."""
    context = {"page": request.page}
    return context
    
    