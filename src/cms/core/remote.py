"""Simple library for opening remote URLs."""


import urllib, urllib2, BaseHTTPServer

from django.http import HttpResponse
from django.utils import simplejson

from cms.core import iteration


__all__ = ("RemoteError", "HttpError", "encode", "open", "prefetch", "open_xml",)


class RemoteError(IOError):
    
    """Exception thrown when a network error prevents a fetch operation."""
    
    
class HttpError(RemoteError):
    
    """Exception thrown when a HTTP error code prevents a fetch operation."""
    
    def __init__(self, reason, response):
        """Creates a new HttpError."""
        super(HttpError, self).__init__(reason)
        self.response = response


response_codes = BaseHTTPServer.BaseHTTPRequestHandler.responses


def encode(data):
    """
    Encodes the given data for transmission.
    
    Strings, dictionaries and tuple sequences are all allowed.
    """
    if isinstance(data, basestring):
        return data
    else:
        return urllib.urlencode(sorted(iteration.iteritems(data)), doseq=True)


def open(url, data=None, query="", headers={}, username="", password="", require_success=True):
    """
    Fetches the given URL, using the parameters provided.
    
    Any data will automatically be encoded and escaped.  Data can be in the form
    of a dictionary or a character string.  Supplying any data will make the
    request use the POST method, otherwise the GET method will be used.
    
    A standard Django HttpResponse will be returned.  If require_success is
    True (the default), then a non-okay status code will result in a HttpError
    being thrown.  Setting this to False will result in the error being returned
    encoded as a HttpResponse.
    """
    # Create the request.
    if data:
        data = encode(data)
    query = encode(query)
    if query:
        url += "?" + query
    request = urllib2.Request(url, data, headers)
    # Create an opener.
    opener = urllib2.build_opener()
    # Create an authentication handler.
    if username or password:
        password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(None, request.get_full_url(), username, password)
        auth_handler = urllib2.HTTPBasicAuthHandler(password_manager)
        opener.add_handler(auth_handler)
    try:
        # Fetch the response.
        content = opener.open(request)
    except urllib2.HTTPError, ex:
        content = ex
        status = ex.code
    except urllib2.URLError, ex:
        # No network connection - go nuts!
        raise RemoteError, ex.reason
    else:
        status = 200
    # Parse the response.
    response = HttpResponse(content.read(), status=status)
    for key, value in content.info().items():
        response[key] = value
    # Check for success.
    if require_success and (response.status_code < 200 or response.status_code >= 300):
        status_code = response.status_code
        reason = response_codes.get(status_code, ["Unknown Error Code", ""])[0]
        error_message = "Error %i (%s): %s" % (status_code, reason, response.content)
        raise HttpError(error_message, response)
    return response
            
    
def open_json(*args, **kwargs):
    """Fetches a JSON document, returning a JSON object."""
    response = open(*args, **kwargs)
    return simplejson.loads(response.content)
    
    