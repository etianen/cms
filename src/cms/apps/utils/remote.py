"""Simple library for opening remote URLs."""


import datetime, urllib, urllib2, BaseHTTPServer

from django.conf import settings
from django.http import HttpResponse

from cms.apps.utils import xml
from cms.apps.utils.models import CachedRemoteResource


class NetworkError(IOError):
    
    """Exception thrown when a network error prevents a fetch operation."""
    
    
class HttpError(NetworkError):
    
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
        return urllib.quote_plus(data)
    else:
        return urllib.urlencode(data, doseq=True)


def _open(request, username="", password=""):
    """Opens the give URL, and returns a HttpResponse."""
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
        raise NetworkError, ex.reason
    else:
        status = 200
    # Parse the response.
    response = HttpResponse(content.read(), status=status)
    for key, value in content.info().items():
        response[key] = value
    return response


def open(url, data="", query="", headers={}, username="", password="", require_success=True, cache=False, cache_timeout=None, prefetch=False):
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
    # Calculate various timestamps.
    now = datetime.datetime.now()
    cache_timeout = cache_timeout or settings.DEFAULT_REMOTE_CACHE_TIMEOUT
    # Some sanity checking.
    if cache and (username or password):
        raise ValueError, "Cannot requests that send data or require authentication."
    if prefetch and not cache:
        raise ValueError, "Only cached requests may be prefetched."
    # Create the request.
    data = encode(data)
    query = encode(query)
    if query:
        url += "?" + query
    request = urllib2.Request(url, data, headers)
    # Process the various cache choices.
    if cache:
        # Access the cached resource.
        try:
            cached_resource = CachedRemoteResource.objects.get_by_request(request)
        except CachedRemoteResource.DoesNotExist:
            # This is the first time the request was made.
            cached_resource = CachedRemoteResource()
            cached_resource.request = request
            cached_resource.timestamp = now - cache_timeout  # Force reload.
        # Reload if expired.
        if cached_resource.timestamp + cache_timeout <= now:
            response = _open(request)
            cached_resource.response = response 
            cached_resource.timestamp = now
        else:
            response = cached_resource.response
        # Update the prefetch expire time.
        cached_resource.prefetch_expires = now + settings.REMOTE_PREFETCH_TIMEOUT
        cached_resource.save()
    else:
        response = _open(request, username=username, password=password)
    # Check for success.
    if require_success and (response.status_code < 200 or response.status_code >= 300):
        status_code = response.status_code
        reason = response_codes.get(status_code, ["Unknown Error Code", ""])[0]
        error_message = "Error %i (%s): %s" % (status_code, reason, response.content)
        raise HttpError(error_message, response)
    return response
            
            
def prefetch():
    """Prefetches all applicable cached responses."""
    now = datetime.datetime.now()
    for cached_resource in CachedRemoteResource.objects.filter(prefetch_expires__gt=now):
        cache_expires = now + (cached_resource.expires - cached_resource.timestamp)
        cached_resource.response = _open(cached_resource.request, require_success=False)
        cached_resource.expires = cache_expires
        cached_resource.save()
            
    
def open_xml(*args, **kwargs):
    """Fetches an XML document, returning an XML object."""
    response = open(*args, **kwargs)
    return xml.parse(response.content)
    
    