"""Simple library for opening remote URLs."""


import datetime, urllib, urllib2, BaseHTTPServer

from django.conf import settings
from django.http import HttpResponse

from cms.apps.utils import xml
from cms.apps.utils.models import CachedResponse


class NetworkError(IOError):
    
    """Exception thrown when a network error prevents a fetch operation."""
    
    
class HttpError(NetworkError):
    
    """Exception thrown when a HTTP error code prevents a fetch operation."""
    
    def __init__(self, reason, status_code):
        """Creates a new HttpError."""
        super(HttpError, self).__init__(reason)
        self.status_code = status_code


response_codes = BaseHTTPServer.BaseHTTPRequestHandler.responses


def encode(data):
    """
    Encodes the given data for transmission.
    
    Strings, dictionaries and tuple sequences are all allowed.
    """
    if isinstance(data, basestring):
        return urllib.quote_plus(data)
    else:
        return urllib.urlencode(data, doseq=True)


def _open(url, data="", query="", headers={}, username="", password="", require_success=True):
    """Opens the give URL, with no caching."""
    # Encode the data.
    data = encode(data)
    query = encode(query)
    # Append any query string.
    if query:
        url += "?" + query
    # Create the request.
    request = urllib2.Request(url, data, headers)
    # Create an opener.
    opener = urllib2.build_opener()
    # Create an authentication handler.
    if username or password:
        password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(None, url, username, password)
        auth_handler = urllib2.HTTPBasicAuthHandler(password_manager)
        opener.add_handler(auth_handler)
    try:
        # Fetch the response.
        content = opener.open(request)
    except urllib2.HTTPError, ex:
        # Made a connection, but the server was not happy.
        if require_success:
            error_message = "Error %i (%s): %s" % (ex.code, response_codes.get(ex.code, ["Unknown Error Code", ""])[0], ex.read())
            raise HttpError(error_message, ex.code)
        content = ex
        status = ex.code
    except urllib2.URLError, ex:
        # No network connection - go nuts!
        raise NetworkError, ex.reason
    else:
        status = 200
    # Parse the response.
    response = HttpResponse(content.read(), status=status)
    for key, value in content.info().items():
        response[key] = value
    return response


def open(url, data="", query="", headers={}, username="", password="", require_success=True, cache=False, prefetch=False):
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
    now = datetime.datetime.now()
    # Some sanity checking.
    if cache and (username or password or data):
        raise ValueError, "Cannot requests that send data or require authentication."
    if prefetch and not cache:
        raise ValueError, "Only cached requests may be prefetched."
    # Process the various cache choices.
    if isinstance(cache, datetime.timedelta):
        cache_expires = now + cache
    elif cache is True:
        cache_expires = now + settings.DEFAULT_RESPONSE_CACHE_TIMEOUT
    elif cache is False:
        return _open(url, data, query, headers, username, password, require_success)
    else:
        raise ValueError, "Cache value must a boolean or a timedelta, %s encountered" % type(prefetch).__name__
    # Process the various prefetch choices.
    if isinstance(prefetch, datetime.timedelta):
        prefetch_expires = now + prefetch
    elif prefetch is True:
        prefetch_expires = now + settings.DEFAULT_RESPONSE_PREFETCH_TIMEOUT
    elif prefetch is False:
        prefetch_expires = None
    else:
        raise ValueError, "Prefetch value must a boolean or a timedelta, %s encountered" % type(prefetch).__name__
    # Attempt to retrieve the cached response.
    try:
        cached_response = CachedResponse.objects.get(url=url)
    except CachedResponse.DoesNotExist:
        # This is the first time this URL has been accessed.
        response = _open(url, data, query, headers, username, password, require_success)
        CachedResponse.objects.create(url=url, response=response, timestamp=now, expires=cache_expires, prefetch_expires=prefetch_expires)
        return response
    else:
        # Reload the response if it has expired.
        if cached_response.expires <= now:
            response = _open(url, data, query, headers, username, password, require_success)
            cached_response.response = response
            cached_response.timestamp = now
            cached_response.expires = cache_expires
        else:
            response = cached_response.response
        # Update the prefetch expirey.
        cached_response.prefetch_expires = prefetch_expires or cached_response.prefetch_expires
        cached_response.save()
        return response
            
    
def open_xml(*args, **kwargs):
    """Fetches an XML document, returning an XML object."""
    response = open(*args, **kwargs)
    return xml.parse(response.content)
    
    