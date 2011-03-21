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
        self._published_id_cache = {}
        self._permalink_cache = {}
        self._published_permalink_cache = {}
        self._homepage_cache = None
        self._published_homepage_cache = None
        
    def add(self, page):
        """Adds the given page to the cache."""
        # Set the cache value.
        self._id_cache[page.id] = page
        if page.permalink:
            self._permalink_cache[page.permalink] = page
        # Set the published cache value.    
        if publication_manager.select_published_active():
            self._published_id_cache[page.id] = page
            if page.permalink:
                self._published_permalink_cache[page.permalink] = page
        
    def remove(self, page):
        """
        Removes the given page from the cache.
        
        If the page is not in the cache, this is a no-op.
        """
        self._id_cache.pop(page.id, None)
        self._published_id_cache.pop(page.id, None)
        if page.permalink:
            self._permalink_cache.pop(page.permalink, None)
            self._published_permalink_cache.pop(page.permalink, None)
            
    def contains_permalink(self, permalink):
        """Checks whether the given permalink is in the cache."""
        if publication_manager.select_published_active():
            return permalink in self._published_permalink_cache
        return permalink in self._permalink_cache
    
    def get_by_permalink(self, permalink):
        """
        Returns the page referenced by the given permalink.
        
        Raises a KeyError if the page does not exist.
        """
        if publication_manager.select_published_active():
            return self._published_permalink_cache[permalink]
        return self._permalink_cache[permalink]
    
    def contains_id(self, id):
        """Checks whether the given page id is in the cache."""
        if publication_manager.select_published_active():
            return id in self._published_id_cache
        return id in self._id_cache
    
    def get_by_id(self, id):
        """
        Returns the page referenced by the given id.
        
        Raises a KeyError if the page does not exist.
        """
        if publication_manager.select_published_active():
            return self._published_id_cache[id]
        return self._id_cache[id]
        
    def get_homepage(self):
        """Returns the cached homepage, or None."""
        if publication_manager.select_published_active():
            return self._published_homepage_cache
        return self._homepage_cache
        
    def set_homepage(self, homepage):
        """Sets the cached homepage."""
        if publication_manager.select_published_active():
            self._published_homepage_cache = homepage
        self._homepage_cache = homepage
    

cache = PageCache()


class PageManager(PageBaseManager):
    
    """Manager for Page objects."""
    
    def get_homepage(self):
        """Returns the site homepage."""
        homepage = cache.get_homepage()
        if homepage is None:
            homepage = self.get(parent=None)
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
            return self.get(id=id)
    
    def get_by_permalink(self, permalink):
        """
        Returns the page referenced by the given permalink.
        
        The result is cached in the page cache.
        """
        try:
            return cache.get_by_permalink(permalink)
        except KeyError:
            return self.get(permalink=permalink)
        
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