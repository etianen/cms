"""Simple library for opening remote URLs."""


import datetime, urllib, urllib2, BaseHTTPServer

from django.conf import settings
from django.http import HttpResponse

from cms.apps.utils import xml, iteration
from cms.apps.utils.models import CachedRemoteResource


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
        return urllib.quote_plus(data)
    else:
        return urllib.urlencode(iteration.sorted_items(data), doseq=True)


def _open(request, log, username="", password=""):
    """Opens the give URL, and returns a HttpResponse."""
    # Log the request.
    if log is not None:
        log.append(request)
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
    return response


def open(url, data="", query="", headers={}, username="", password="", require_success=True, cache=False, cache_timeout=None, log=None):
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
        raise ValueError, "Cannot requests that require authentication."
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
        # Reload if expired.
        if (cached_resource.last_updated is None) or (cached_resource.last_updated + cache_timeout <= now):
            response = _open(request, log)
            cached_resource.response = response 
            cached_resource.last_updated = now
        else:
            response = cached_resource.response
        # Update the last accessed time.
        cached_resource.last_accessed = now
        cached_resource.save()
    else:
        response = _open(request, log, username=username, password=password)
    # Check for success.
    if require_success and (response.status_code < 200 or response.status_code >= 300):
        status_code = response.status_code
        reason = response_codes.get(status_code, ["Unknown Error Code", ""])[0]
        error_message = "Error %i (%s): %s" % (status_code, reason, response.content)
        raise HttpError(error_message, response)
    return response
            
            
def prefetch(log=None, fail_silently=False, prefetch_timeout=None):
    """Prefetches all applicable cached responses."""
    now = datetime.datetime.now()
    prefetch_timeout = prefetch_timeout or settings.DEFAULT_REMOTE_PREFETCH_TIMEOUT
    prefetch_threshold = now - prefetch_timeout
    for cached_resource in CachedRemoteResource.objects.filter(last_accessed__gt=prefetch_threshold):
        try:
            cached_resource.response = _open(cached_resource.request, log)
        except RemoteError:
            if not fail_silently:
                raise
        else:
            cached_resource.last_updated = now
            cached_resource.save()
            
    
def open_xml(*args, **kwargs):
    """Fetches an XML document, returning an XML object."""
    response = open(*args, **kwargs)
    return xml.parse(response.content)
    
    