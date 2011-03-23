"""Views used by the CMS."""

from django.shortcuts import render
from django.views.generic import DetailView


def handler500(request):
    """Renders a pretty error page."""
    response = render(request, "500.html", {})
    response.status_code = 500
    return response
    
    
class PageView(DetailView):
    
    """A generic view that displays a detail page for a PageBase instance."""
    
    slug_field = "url_title"
    
    def get_context_data(self, **kwargs):
        """Sets the page's SEO information in the context."""
        context = self.object.get_context_data()
        context.update(kwargs)
        context["page"] = self.object
        return super(PageView, self).get_context_data(**context)