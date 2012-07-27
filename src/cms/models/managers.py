"""Model managers used by the pages application."""


from __future__ import with_statement

import threading, contextlib

from django.db import models


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
        super(PublicationManager, self).__init__()
        self._stack = []
        
    def begin(self, select_published):
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
            return False
        
    def end(self):
        """Ends a block of publication control."""
        try:
            self._stack.pop()
        except IndexError:
            raise PublicationManagementError, "There is no active block of publication management."
        
    @contextlib.contextmanager
    def select_published(self, select_published):
        """Marks a block of publication management."""
        self.begin(select_published)
        try:
            yield
        except:
            raise
        finally:
            self.end()
            
    
# A single, thread-safe publication manager.
publication_manager = PublicationManager()


class PublishedBaseManager(models.Manager):
    
    """Manager that fetches published models."""
    
    use_for_related_fields = True
    
    def select_published(self, queryset):
        """
        Filters the given queryset to only include published items.
        
        Override this in subclasses for more specific publication filtering.
        """
        return queryset
    
    def get_query_set(self):
        """"Returns the queryset, filtered if appropriate."""
        queryset = super(PublishedBaseManager, self).get_query_set()
        if publication_manager.select_published_active():
            queryset = self.select_published(queryset)
        return queryset
    
    
class OnlineBaseManager(PublishedBaseManager):
    
    """Publication manager that uses a simple online/offline flag."""
    
    def select_published(self, queryset):
        """
        Filters the given queryset to only include items marked as online.
        """
        queryset = super(OnlineBaseManager, self).select_published(queryset)
        return queryset.filter(is_online=True)
    
    
class SearchMetaBaseManager(OnlineBaseManager):
    
    """Publication manager for SearchMetaBase models."""
    
    
class PageBaseManager(SearchMetaBaseManager):
    
    """Publication manager for SearchMetaBase models."""