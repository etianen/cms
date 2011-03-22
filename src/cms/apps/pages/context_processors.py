"""Context processors used by the pages application."""


def page(request):
    """Places the current page in the template."""
    page = request.page
    homepage = page.homepage
    context = {
        "page": page,
        "homepage": homepage,
        "is_homepage": homepage.get_absolute_url() == request.path,
    }
    return context
    
    