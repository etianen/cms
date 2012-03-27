"""Model managers used by the pages application."""


import threading

from django.core.signals import request_finished

from cms.core.models.managers import PublishedBaseManager, publication_manager
    
    
class PageCache(threading.local):
    
    """A local cache of pages, used to seriously cut down on database queries."""
    
    def __init__(self):
        """Initializes the PageCache."""
        super(PageCache, self).__init__()
        self.clear()
        # Add the cleanup handler.
        request_finished.connect(self.handle_request_finished)
        
    def clear(self):
        """Clears the page cache."""
        self._cache = {}  # pylint: disable=W0201
        self._homepage_cache = None  # pylint: disable=W0201
        
    def put(self, page):
        """Adds the given page to the cache."""
        # Set the cache value.
        self._cache[page.id] = page
        if page.permalink:
            self._cache[page.permalink] = page
        
    def remove(self, page):
        """
        Removes the given page from the cache.
        
        If the page is not in the cache, this is a no-op.
        """
        self._cache.pop(page.id, None)
        if page.permalink:
            self._cache.pop(page.permalink, None)
    
    def _needs_reload(self, page):
        """Checks whether the page was created in an insufficient publication context."""
        return not page._select_published_active and publication_manager.select_published_active()
    
    def get(self, id):
        """
        Returns the page referenced by the given id or permalink.
        
        Raises a KeyError if the page is not in the cache.
        """
        page = self._cache[id]
        if self._needs_reload(page):
            raise KeyError(id)
        return page
        
    def put_homepage(self, homepage):
        """Stores the given homepage."""
        self._homepage_cache = homepage  # pylint: disable=W0201
        
    def get_homepage(self):
        """
        Returns the cached homepage.
        
        Raises a KeyError if the page is not in the cache.
        """
        if self._homepage_cache is None:
            raise KeyError("__homepage__")
        if self._needs_reload(self._homepage_cache):
            raise KeyError("__homepage__")
        return self._homepage_cache
        
    def handle_request_finished(self, **kwargs):
        """Signal handler for end of request."""
        self.clear()


class PageManager(PublishedBaseManager):
    
    """Manager for Page objects."""
    
    def __init__(self, *args, **kwargs):
        """Initializes the PageManager."""
        super(PageManager, self).__init__(*args, **kwargs)
        self.cache = PageCache()
    
    def get_by_id(self, id):
        """
        Returns the page referenced by the given id.
        
        If no page is found, a Page.DoesNotExist will be raised.
        """
        id = int(id)
        try:
            return self.cache.get(id)
        except KeyError:
            return self.get(id=id)