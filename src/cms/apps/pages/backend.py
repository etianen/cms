"""The backend implementation for the app."""

from django.core import urlresolvers
from django.contrib.contenttypes.models import ContentType

from cms.core.db import locked
from cms.core.pages import BackendBase
from cms.apps.historylinks.models import HistoryLink
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
    
    def get(self, request, id):
        """Returns the page with the given id."""
        try:
            return Page.objects.get_page(id)
        except Page.DoesNotExist:
            return None
    
    def reverse(self, request, page, view_name, args, kwargs):
        """Reverses the given URL in the context of the given page."""
        return page.reverse(view_name, args, kwargs)
        
    def resolve(self, request, page, path_info):
        """Attempts to resolve the given path info to a request handler."""
        return urlresolvers.resolve(path_info, page.content.urlconf)
    
    def _swap(self, page, other):
        """Swaps over two pages."""
        with locked(Page, ContentType, HistoryLink):
            page_order = page.order
            other_order = other.order
            page.order = other_order
            other.order = page_order
            page.save()
            other.save()
    
    can_move = True
        
    def move_up(self, request, page):
        """Moves the given page up, relative to it's siblings."""
        if page.parent is not None:
            try:
                other = page.prev
            except IndexError:
                # Impossible to move pag up or down because it already is at the top or bottom!
                pass
            else:
                self._swap(page, other)

    def move_down(self, request, page):
        """Moves the given page down, relative to it's siblings."""
        if page.parent is not None:
            try:
                other = page.next
            except IndexError:
                # Impossible to move pag up or down because it already is at the top or bottom!
                pass
            else:
                self._swap(page, other)