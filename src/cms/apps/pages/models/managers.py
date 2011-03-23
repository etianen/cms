"""Model managers used by the pages application."""


from __future__ import with_statement

import threading

from cms.core.models.managers import PageBaseManager, publication_manager
    
    
class PageCache(threading.local):
    
    """A local cache of pages, used to seriously cut down on database queries."""
    
    def __init__(self):
        """Initializes the PageCache."""
        self.clear()
        
    def clear(self):
        """Clears the page cache."""
        self._cache = {}
        self._homepage_cache = None
        
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
        self._homepage_cache = homepage
        
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


class PageManager(PageBaseManager):
    
    """Manager for Page objects."""
    
    def __init__(self, *args, **kwargs):
        """Initializes the PageManager."""
        super(PageManager, self).__init__(*args, **kwargs)
        self.cache = PageCache()
    
    def get_homepage(self):
        """
        Returns the homepage.
        
        If there is no homepage, a Page.DoesNotExist will be raised.
        """
        # Try to use the cache.
        try:
            return self.cache.get_homepage()
        except KeyError:
            pass
        # Load in the homepage.
        homepage = self.get(parent=None)
        self.cache.put_homepage(homepage)
        return homepage
        
    def get_by_path(self, path):
        """
        Returns the page that best matches the given URL.
        
        If there is not match, a Page.DoesNotExist will be raised.
        """
        page = self.get_homepage()
        if page is not None:
            # Get the most exact page match.
            for slug in path.strip("/").split("/"):
                matched = False
                for child in page.children:
                    if child.url_title == slug:
                        page = child
                        matched = True
                if not matched:
                    break
        return page
    
    def get_page(self, id):
        """
        Returns the page referenced by the given id.
        
        If not page is found, a Page.DoesNotExist will be raised.
        
        This general-perpose method accepts three possible types of id.  If
        given an integer or basestring, then the page will be looked up by id
        or permalink respectively.  If passed a page instance, then the instance
        will be returned.
        
        The result is cached in the page cache.
        """
        # Accept Page arguments.
        if isinstance(id, self.model):
            return id
        # Try the cache.
        try:
            return self.cache.get(id)
        except KeyError:
            pass
        # Accept int arguments.
        try:
            id = int(id)
        except (ValueError, TypeError):
            pass
        else:
            return self.get(id=id)
        # Accept basestring arguments.
        if isinstance(id, basestring):
            return self.get(permalink=id)
        # Complain about an unrecognised argument type.
        raise TypeError, "Expected Page, int or basestring.  Found %s." % type(id).__name__