"""Views used by the CMS."""

from django.shortcuts import render
from django.views.generic import DetailView


def handler500(request):
    """Renders a pretty error page."""
    response = render(request, "500.html", {})
    response.status_code = 500
    return response
    
    
class PageMixin(object):
    
    """A generic view that adds in SEO information for a specified page."""
    
    def get_page(self):
        """Returns the current page."""
        return self.object
    
    def get_context_data(self, **kwargs):
        """Sets the page's SEO information in the context."""
        context = super(PageMixin, self).get_context_data(**kwargs)
        context.update(self.get_page().get_context_data())
        return context
        
        
class PageDetailView(PageMixin, DetailView):
    
    """A generic view that provides a detail view for a page."""
    
    slug_field = "url_title"