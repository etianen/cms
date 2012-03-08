"""The backend implementation for the app."""

from django.core import urlresolvers
from django.conf import settings

import optimizations

from cms.apps.pages.models import Page
from cms.loader import load_object


class PageBackend(object):
    
    """A page backend that uses Page models."""
    
    model = Page
    
    def filter_for_site(self, request, queryset):
        """Filters the given queryset to only show pages that belong in this site."""
        return queryset
    
    def get_homepage(self, request):
        """Returns the site homepage."""
        try:
            return Page.objects.get(parent=None)
        except Page.DoesNotExist:
            return None
        
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
    
    def get_navigation(self, request, level):
        """Returns the navigation list for the given level (zero-indexed)."""
        page = self.get_current(request)
        try:
            section = page.breadcrumbs[level]
        except IndexError:
            return []
        else:
            return section.navigation
    
    def get(self, request, id):
        """Returns the page with the given id."""
        if isinstance(id, int):
            try:
                return self.model.objects.get(id=id)
            except self.model.DoesNotExist:
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
        # Get a lock on the pages.
        page, other = self.model.objects.filter(pk__in=(page.pk, other.pk)).select_for_update()
        # Swap them!
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
                
    def mount(self, request):
        """Mounts this backend on the given request."""
        request.pages = MountedBackend(self, request)
                
                
class MountedBackend(object):
    
    """A page backend mounted on a request."""
    
    def __init__(self, backend, request):
        """Initializes the MountedBackend."""
        self.backend = backend
        self.request = request
    
    @property
    def all(self):
        """Returns all pages in the site."""
        return self.backend.filter_for_site(self.request, self.backend.model)
    
    def filter_for_site(self, queryset):
        """Filters the given queryset to only show pages that belong in this site."""
        return self.backend.filter_for_site(self.request, queryset)
    
    @optimizations.cached_property
    def homepage(self):
        """The current homepage."""
        return self.backend.get_homepage(self.request)
    
    @optimizations.cached_property
    def is_homepage(self):
        """Whether the current request is for the site homepage."""
        return self.request.path == self.homepage.get_absolute_url()
    
    def get(self, id):
        """Returns the page with the given id, or None."""
        return self.backend.get(self.request, id)
        
    @optimizations.cached_property
    def current(self):
        """Returns the current best-matched page."""
        return self.backend.get_current(self.request)
        
    def reverse(self, page, view_name="index", *args, **kwargs):
        """
        Reverses the given url in the context of the given page.
        
        The page can be a page instance, or a page id.
        """
        return self.backend.reverse(self.request, page, view_name, args, kwargs)
    
    # Navigation.
    
    def get_navigation(self, level=0):
        """Returns the navigation list for the given level (zero-indexed)."""
        return self.backend.get_navigation(self.request, level)
    
    @optimizations.cached_property
    def nav_primary(self):
        """Returs the primary navigation for the site."""
        return self.get_navigation(0)
    
    @optimizations.cached_property
    def nav_secondary(self):
        """Returns the secondary navigation for the site."""
        return self.get_navigation(1)
        
    @optimizations.cached_property
    def nav_tertiary(self):
        """Returns the tertiary navigation for the site."""
        return self.get_navigation(2)


_backend_cache = None
        
def get_backend():
    """Returns the page backend, as specified in the settings."""
    global _backend_cache
    backend_name = getattr(settings, "PAGE_BACKEND", None)
    # Simple case - no backend.
    if backend_name is None:
        return None
    # Try to use the cached backend.
    if _backend_cache is not None:
        return _backend_cache
    # Use load up the backend.
    backend_cls = load_object(backend_name)
    backend = backend_cls()
    _backend_cache = backend
    return backend