"""General utility models."""


import urllib2

from django.db import models
from django.http import HttpResponse

from cms.apps.utils import xml, iteration


def headers_to_xml(headers):
    """Encodes the given headers as XML."""
    return xml.create("headers").append_all(xml.create("header", name=name, content=content) for name, content in sorted(iteration.iteritems(headers))).render()


def xml_to_headers(headers_xml):
    """Decodes the given XML to headers."""
    return dict((header.name, header.content) for header in xml.parse(headers_xml).filter("header"))


class CachedRemoteResouceManager(models.Manager):
    
    """Manages remote requests."""
    
    def get_by_request(self, request):
        """Loads the cached remote resource for the given request."""
        return self.get(request_url=request.get_full_url(),
                        request_headers_xml=headers_to_xml(request.header_items()),
                        request_content=request.get_data())


class CachedRemoteResource(models.Model):
    
    """A remote request that was cached by the application."""
    
    objects = CachedRemoteResouceManager()
    
    # Request encoding.
    
    request_url = models.URLField(db_index=True,
                                  help_text="The URL of the response that was cached.")
    
    request_headers_xml = models.TextField(help_text="An XML representation of the headers of the cached request.")
    
    def get_request_headers(self):
        """Returns the headers of the cached request."""
        return xml_to_headers(self.request_headers_xml)
    
    def set_request_headers(self, headers):
        """Sets the headers of the cached request."""
        self.request_headers_xml = headers_to_xml(headers)
        
    request_headers = property(get_request_headers,
                               set_request_headers,
                               doc="The headers of the cached request.")
        
    request_content = models.TextField(help_text="The content of the cached request.")
        
    def get_request(self):
        """Returns the cached request."""
        return urllib2.Request(self.request_url, self.request_content, self.request_headers)
    
    def set_request(self, request):
        """Sets the cached request."""
        self.request_url = request.get_full_url()
        self.request_headers = request.header_items()
        self.request_content = request.get_data()
        
    request = property(get_request,
                       set_request,
                       doc="The cached request.")
    
    # Response encoding.
    
    response_code = models.PositiveIntegerField(help_text="The status code of the cached response.")
    
    response_headers_xml = models.TextField(help_text="An XML representation of the headers of the cached response.")
    
    def get_response_headers(self):
        """Returns the headers of the cached response."""
        return xml_to_headers(self.response_headers_xml)
    
    def set_response_headers(self, headers):
        """Sets the headers of the cached response."""
        self.response_headers_xml = headers_to_xml(headers) 
            
    response_headers = property(get_response_headers,
                                set_response_headers,
                                doc="The headers of the cached response.")
    
    response_content = models.TextField(help_text="The content of the cached response.")
    
    def get_response(self):
        """Returns the cached HttpResponse."""
        response = HttpResponse(self.response_content, status=self.response_code)
        response._headers = self.response_headers
        return response
            
    def set_response(self, response):
        """Sets the cached HttpResponse."""
        self.response_content = response.content
        self.response_code = response.status_code
        self.response_headers = dict(response.items())
        
    response = property(get_response,
                        set_response,
                        doc="The cached HttpResponse.")
    
    # Timestamps.
    
    last_updated = models.DateTimeField(help_text="The time that the this resource was lasted fetched from the remote server.")
    
    last_accessed = models.DateTimeField(db_index=True,
                                         help_text="The time that this resource was last accessed by the application.")
    
    