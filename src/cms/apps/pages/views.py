"""Core views used by the CMS."""


from cms.apps.pages.models import Page
        
        
def handler404(request):
    """Renders a pretty error page."""
    page = Page.objects.get_by_path(request.path)
    context = {"title": "Page Not Found"}
    response = page.content.render_to_response(request, "404.html", context)
    response.status_code = 404
    return response
        

def handler500(request):
    """Renders a pretty error page."""
    page = Page.objects.get_by_path(request.path)
    context = {"title": "Server Error"}
    response = page.content.render_to_response(request, "500.html", context)
    response.status_code = 500
    return response

