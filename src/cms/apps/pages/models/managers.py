"""Model managers used by the pages application."""


from __future__ import with_statement

import threading

from cms.core.models.managers import PageBaseManager, publication_manager
    
    
class PageCache(threading.local):
    
    """
    A local cache of pages, used to seriously cut down on database queries.
    """
    
    def __init__(self):
        """Initializes the PageCache."""
        self.clear()
        
    def clear(self):
        """Clears the page cache."""
        self._id_cache = {}
        self._permalink_cache = {}
        self._homepage_cache = None
        
    def add(self, page):
        """Adds the given page to the cache."""
        # Set the cache value.
        self._id_cache[page.id] = page
        if page.permalink:
            self._permalink_cache[page.permalink] = page
        
    def remove(self, page):
        """
        Removes the given page from the cache.
        
        If the page is not in the cache, this is a no-op.
        """
        self._id_cache.pop(page.id, None)
        if page.permalink:
            self._permalink_cache.pop(page.permalink, None)
    
    def _filter_unpublished(self, page):
        """
        Checks whether the page was retrieved under an adequate publication context.
        
        If it was, the page is returned. Otherwise, None is returned.
        """
        if page is not None and not page._select_published_active and publication_manager.select_published_active():
            return None
        return page
    
    def get_by_permalink(self, permalink):
        """
        Returns the page referenced by the given permalink.
        
        Returns None if the page is not in the cache.
        """
        return self._filter_unpublished(self._permalink_cache.get(permalink))
    
    def get_by_id(self, id):
        """
        Returns the page referenced by the given id.
        
        Returns None if the page is not in the cache.
        """
        return self._filter_unpublished(self._id_cache.get(id))
        
    def get_homepage(self):
        """Returns the cached homepage, or None."""
        return self._filter_unpublished(self._homepage_cache)
        
    def set_homepage(self, homepage):
        """Sets the cached homepage."""
        self._homepage_cache = homepage
    

cache = PageCache()


class PageManager(PageBaseManager):
    
    """Manager for Page objects."""
    
    def add_deferrals(self, qs):
        """Adds in the appropriate field deferrals to the querysey."""
        return qs.defer("content_data", "meta_description", "meta_keywords")
    
    def get_homepage(self):
        """Returns the site homepage."""
        homepage = cache.get_homepage()
        if homepage is None:
            homepage = self.add_deferrals(self.all()).get(parent=None)
            cache.set_homepage(homepage)
        return homepage
    
    def get_by_id(self, id):
        """
        Returns the page referenced by the given id.
        
        The result is cached in the page cache.
        """
        try:
            return cache.get_by_id(id)
        except KeyError:
            return self.add_deferrals(self.all()).get(id=id)
    
    def get_by_permalink(self, permalink):
        """
        Returns the page referenced by the given permalink.
        
        The result is cached in the page cache.
        """
        try:
            return cache.get_by_permalink(permalink)
        except KeyError:
            return self.add_deferrals(self.all()).get(permalink=permalink)
        
    def get_by_path(self, path):
        """Returns the page that best matches the given URL."""
        page = self.get_homepage()
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
        
        This general-perpose method accepts three possible types of id.  If
        given an integer or basestring, then the page will be looked up by id
        or permalink respectively.  If passed a page instance, then the instance
        will be returned.
        
        The result is cached in the page cache.
        """
        # Accept Page arguments.
        if isinstance(id, self.model):
            return id
        # Accept int arguments.
        try:
            id = int(id)
        except (ValueError, TypeError):
            pass
        else:
            return self.get_by_id(id)
        # Accept basestring arguments.
        if isinstance(id, basestring):
            return self.get_by_permalink(id)
        # Complain about an unrecognised argument type.
        raise TypeError, "Expected Page, int or basestring.  Found %s." % type(id).__name__