"""Page management utilities."""

import abc

from django.conf import settings

import optimizations

from cms.core.loader import load_object


class BackendBase(object):
    
    """Base class for a page backend implementation."""
    
    __metaclass__ = abc.ABCMeta
    
    # The primary model of the backend.
    model = None
    
    def get_all(self, request):
        """Returns all the pages in the site."""
        return self.model._default_manager.all()
    
    @abc.abstractmethod
    def get_homepage(self, request):
        """Returns the current homepage, or None."""
        raise NotImplementedError
    
    @abc.abstractmethod    
    def get_current(self, request):
        """Returns the current best-matched page, or None."""
        raise NotImplementedError
    
    def get(self, request, id):
        """Returns the page matching the given id, or None."""
        return self.model._default_manager.get(pd=id)
        
    @abc.abstractmethod
    def reverse(self, request, page, view_name, args, kwargs):
        """Reverses the given url in the context of the given page."""
        raise NotImplementedError
    
    # Navigation.
    
    def get_navigation(self, request, level):
        """Returns the navigation list for the given level (zero-indexed)."""
        page = self.get_current(request)
        try:
            section = page.breadcrumbs[level]
        except IndexError:
            return []
        else:
            return section.navigation
    
    # Does this backend support moving pages around?    
    can_move = False
    
    def move_up(self, request, page):
        """Moves the given page up, relative to it's siblings."""
        raise NotImplementedError
        
    def move_down(self, request, page):
        """Moves the given page down, relative to it's siblings."""
        raise NotImplementedError
        
    # Request handling.
    
    def mount(self, request):
        """Mounts this backend on the given request."""
        request.pages = MountedBackend(self, request)
    
    @abc.abstractmethod    
    def resolve(self, request, page, path_info):
        """Attempts to resolve the given path info to a request handler."""
        raise NotImplementedError
        
    
class MountedBackend(object):
    
    """A page backend mounted on a request."""
    
    def __init__(self, backend, request):
        """Initializes the MountedBackend."""
        self.backend = backend
        self.request = request
    
    @property
    def all(self):
        """Returns all pages in the site."""
        return self.backend.get_all(self.request)
    
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