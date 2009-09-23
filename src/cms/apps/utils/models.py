"""General utility models."""


from django.db import models
from django.http import HttpResponse

from cms.apps.utils import xml


class CachedResponse(models.Model):
    
    """A remote request that was cached by the application."""
    
    url = models.URLField(unique=True,
                          help_text="The URL of the response that was cached.")
    
    # Response encoding.
    
    status_code = models.PositiveIntegerField(help_text="The status code of the cached response.")
    
    headers_xml = models.TextField(help_text="An XML representation of the headers of the cached response.")
    
    def get_headers(self):
        """Returns the headers of the cached response."""
        return dict((header.name, header.content) for header in xml.parse(self.headers_xml).filter("header"))
    
    def set_headers(self, headers):
        """Sets the headers of the cached response."""
        self.headers_xml = xml.create("headers").append_all(xml.create("header", name=name, value=value) for name, value in headers.iteritems())
            
    headers = property(get_headers,
                       set_headers,
                       doc="The headers of the cached response.")
    
    content = models.TextField(help_text="The content of the cached response.")
    
    def get_response(self):
        """Returns the cached HttpResponse."""
        response = HttpResponse(self.content, status=self.status_code)
        response._headers = self.headers
        return response
            
    def set_response(self, response):
        """Sets the cached HttpResponse."""
        self.content = response.content
        self.status_code = response.status_code
        self.headers = response._headers
        
    response = property(get_response,
                        set_response,
                        doc="The cached HttpResponse.")
    
    # Timestamps.
    
    timestamp = models.DateTimeField(help_text="The time that the this response was cached.")
    
    expires = models.DateTimeField(help_text="The time at which point this response requires reloading.")
    
    prefetch_expires = models.DateTimeField(blank=True,
                                            null=True,
                                            db_index=True,
                                            help_text="The time at which this URL should no longer be prefetched.  If NULL, then this URL should never be prefetched.  Please note: the prefetch_urls admin command must be added the the server cronjob for this feature to work.")
    
    