"""Views used by the pages app."""

from cms.core.views import PageView


class CurrentPageView(PageView):
    
    """View that renders the current page."""
    
    template_name = "pages/base.html"
    
    def get_object(self, queryset=None):
        """Returns the current page."""
        return self.kwargs["page"]