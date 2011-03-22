"""Views used by the pages application."""

from cms.core.views import PageView


class CurrentPageView(PageView):
    
    template_name = "pages/base.html"
    
    content_object_name = "page"
    
    def get_object(self, queryset=None):
        """Retrieves the current page."""
        return self.request.page