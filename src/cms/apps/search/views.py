"""Views used by the search application."""


def index(request):
    """Renders the search results page."""
    page = request.page
    return page.render_to_response(request, "search/index.html")

