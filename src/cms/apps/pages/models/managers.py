"""Model managers used by the pages application."""


from __future__ import with_statement

import threading, contextlib

from django.contrib.sites.models import Site
from django.db import models
from django.core.validators import slug_re


class PublicationManagementError(Exception):
    
    """
    Exception thrown when something goes wrong with publication management.
    """


class PublicationManager(threading.local):
    
    """
    Tracks a thread-local state of whether querysets should be filtered based on
    publication state.
    
    By default, unpublished content will be filtered out.
    """
    
    def __init__(self):
        """Initializes the PublicationManager."""
        self._stack = []
        
    def _begin(self, select_published):
        """Starts a block using the given publication setting."""
        self._stack.append(select_published)
        
    def select_published_active(self):
        """
        Returns True if querysets should be filtered to exclude unpublished
        content.
        """
        try:
            return self._stack[-1]
        except IndexError:
            return True
        
    def _end(self):
        """Ends a block of publication control."""
        try:
            self._stack.pop()
        except IndexError:
            raise PublicationManagementError, "There is no active block of publication management."
        
    @contextlib.contextmanager
    def select_published(self, select_published):
        """Marks a block of publication management."""
        self._begin(select_published)
        try:
            yield
        except:
            raise
        finally:
            self._end()
            
    
# A single, thread-safe publication manager.
publication_manager = PublicationManager()


class PublishedModelManager(models.Manager):
    
    """Manager that fetches published models."""
    
    use_for_related_fields = True
    
    def get_query_set(self):
        """"Returns the queryset, filtered if appropriate."""
        queryset = super(PublishedModelManager, self).get_query_set()
        if publication_manager.select_published_active():
            queryset = self.model.select_published(queryset)
        return queryset
    
    
class PageBaseManager(PublishedModelManager):
    
    """Base managed for pages."""
    
    def get_query_set(self):
        """Returns the filtered query set."""
        queryset = super(PageBaseManager, self).get_query_set()
        queryset = queryset.filter(site=Site.objects.get_current())
        return queryset
    
    
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
        self._id_cache[page.id] = page
        if page.permalink:
            self._permalink_cache[page.permalink] = page
        
    def remove(self, page):
        """
        Removes the given page from the cache.
        
        If the page is not in the cache, this is a no-op.
        """
        try:
            del self._id_cache[page.id]
        except KeyError:
            pass
        if page.permalink:
            try:
                del self._permalink_cache[page.permalink]
            except KeyError:
                pass
            
    def contains_permalink(self, permalink):
        """Checks whether the given permalink is in the cache."""
        return permalink in self._permalink_cache
    
    def get_by_permalink(self, permalink):
        """
        Returns the page referenced by the given permalink.
        
        Raises a KeyError if the page does not exist.
        """
        return self._permalink_cache[permalink]
    
    def contains_id(self, id):
        """Checks whether the given page id is in the cache."""
        return id in self._id_cache
    
    def get_by_id(self, id):
        """
        Returns the page referenced by the given id.
        
        Raises a KeyError if the page does not exist.
        """
        return self._id_cache[id]
    

cache = PageCache()


class PageManager(PageBaseManager):
    
    """Manager for Page objects."""
    
    def get_homepage(self):
        """Returns the site homepage."""
        if cache._homepage_cache is None:
            cache._homepage_cache = self.get(parent=None)
        return cache._homepage_cache
    
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
    
    def expand_page_url(self, slug):
        """
        Attempts to convert a page shortcut into a full URL.
        
        If the slug contains a forward slash, then it is returned unchanged.
        
        Otherwise, a page is looked up using the URL as a page permalink for a
        page id.  If successful, the page URL is returned.  Otherwise, the slug
        is returned unchanged.
        """
        if not slug_re.search(slug):
            return slug
        try:
            page = self.get_page(slug)
        except self.model.DoesNotExist:
            return slug
        else:
            return page.get_absolute_url()
        
        