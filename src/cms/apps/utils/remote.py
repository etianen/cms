"""Simple library for fetching remote URLs."""


import urllib, urllib2, BaseHTTPServer

from django.http import HttpResponse

from cms.apps.utils import xml


class NetworkError(IOError):
    
    """Exception thrown when a network error prevents a fetch operation."""
    
    
class HttpError(IOError):
    
    """Exception thrown when a HTTP error code prevents a fetch operation."""


response_codes = BaseHTTPServer.BaseHTTPRequestHandler.responses


def fetch(url, post={}, get={}, headers={}, username="", password="", require_success=True, timeout=None):
    """
    Fetches the given URL, using the parameters provided.
    
    Any get data will automatically be encoded and appended to the URL.
    
    A standard Django HttpResponse will be returned.  If require_success is
    True (the default), then a non-okay status code will result in a HttpError
    being thrown.  Setting this to False will result in the error being returned
    encoded as a HttpResponse.   
    """
    # Encode the query string, if any.
    if get:
        if "?" in url:
            url += "&"
        else:
            url += "?"
        if not isinstance(get, basestring):
            get = urllib.urlencode(get)
        url += get
    # Encode the POST data.
    if not isinstance(post, basestring):
        post = urllib.urlencode(post)
    # Create the request.
    request = urllib2.Request(url, post, headers)
    # Create an opener.
    opener = urllib2.build_opener()
    # Create an authentication handler.
    if username:
        password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(None, url, username, password)
        auth_handler = urllib2.HTTPBasicAuthHandler(password_manager)
        opener.add_handler(auth_handler)
    try:
        # Fetch the response.
        content = opener.open(request, timeout=timeout)
    except urllib2.HTTPError, ex:
        # Made a connection, but the server was not happy.
        if require_success:
            raise HttpError, "Error %i (%s): %s" % (ex.code, response_codes.get(ex.code, ["Unknown Error Code", ""])[0], ex.read())
        content = ex
        status = ex.code
    except urllib2.URLError, ex:
        # No network connection - go nuts!
        raise NetworkError, ex.reason
    else:
        status = 200
    # Parse the response.
    response = HttpResponse(content, status=status)
    for key, value in content.info().items():
        response[key] = value
    return response
    
    
def fetch_xml(*args, **kwargs):
    """Fetches an XML document, returning an XML object."""
    response = fetch(*args, **kwargs)
    return xml.parse(response.content)
    
    