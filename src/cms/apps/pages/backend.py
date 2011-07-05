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
        # Try to use the cache.
        try:
            return Page.objects.cache.get_homepage()
        except KeyError:
            pass
        # Load in the homepage.
        try:
            homepage = Page.objects.get(parent=None)
        except Page.DoesNotExist:
            return None
        else:
            Page.objects.cache.put_homepage(homepage)
            return homepage
        
    def get_current(self, request):
        """Returns the best-matched page, or None"""
        page = self.get_homepage(request)
        if page is not None:
            # Get the most exact page match.
            for slug in request.path_info.strip("/").split("/"):
                matched = False
                for child in page.children:
                    if child.url_title == slug:
                        page = child
                        matched = True
                if not matched:
                    break
        return page
    
    def get(self, request, id):
        """Returns the page with the given id."""
        if isinstance(id, int):
            try:
                return Page.objects.get_by_id(id)
            except Page.DoesNotExist:
                return None
        elif isinstance(id, basestring):
            try:
                return Page.objects.filter(permalink=id)[0]
            except IndexError:
                return None
        else:
            raise ValueError("Page id should be a basestring or an int, not {!r}".format(id))
    
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