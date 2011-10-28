"""Views used by the CMS."""

from django.shortcuts import render
from django.views import generic


def handler500(request):
    """Renders a pretty error page."""
    response = render(request, "500.html", {})
    response.status_code = 500
    return response
    
    
class TextTemplateView(generic.TemplateView):

    """A template view that returns a text/plain response."""

    content_type = "text/plain; charset=utf-8"
    
    def render_to_response(self, context, **kwargs):
        """Dispatches the request."""
        kwargs.setdefault("content_type", self.content_type)
        return super(TextTemplateView, self).render_to_response(context, **kwargs)
    
    
class EntityContextMixin(object):
    
    """Generates the context for an entity detail page."""
    
    def get_context_data(self, **kwargs):
        """Adds in the additional entity context data."""
        context = super(EntityContextMixin, self).get_context_data(**kwargs)
        defaults = self.object.get_context_data()
        defaults.update(context)
        return defaults
    
    
class EntityDetailView(EntityContextMixin, generic.DetailView):
    
    """A simple entity detail view."""