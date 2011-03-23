"""The backend implementation for the app."""

from django.conf import settings
from django.core import urlresolvers

from cms.core.pages import BackendBase
from cms.apps.pages.models import Page


class PageBackend(BackendBase):
    
    """A page backend that uses Page models."""
    
    model = Page
    
    def get_homepage(self, request):
        """Returns the site homepage."""
        try:
            return Page.objects.get_homepage()
        except Page.DoesNotExist:
            return None
        
    def get_current(self, request):
        """Returns the best-matched page, or None"""
        try:
            return Page.objects.get_by_path(request.path_info)
        except Page.DoesNotExist:
            return None
    
    def get(self, id):
        """Returns the page with the given id."""
        return Page.objects.get_page(id)
    
    def reverse(self, request, page, view_name, args, kwargs):
        """Reverses the given URL in the context of the given page."""
        return page.reverse(view_name, args, kwargs)
        
    def resolve(self, request, page, path_info):
        """Attempts to resolve the given path info to a request handler."""
        return urlresolvers.resolve(path_info, page.content.urlconf)