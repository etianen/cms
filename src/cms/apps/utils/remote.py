"""Simple library for opening remote URLs."""


import urllib, urllib2, BaseHTTPServer

from django.http import HttpResponse

from cms.apps.utils import xml


class NetworkError(IOError):
    
    """Exception thrown when a network error prevents a fetch operation."""
    
    
class HttpError(NetworkError):
    
    """Exception thrown when a HTTP error code prevents a fetch operation."""
    
    def __init__(self, reason, status_code):
        """Creates a new HttpError."""
        super(HttpError, self).__init__(reason)
        self.status_code = status_code


response_codes = BaseHTTPServer.BaseHTTPRequestHandler.responses

GET = "GET"

POST = "POST"


def open(url, data="", headers={}, method=None, username="", password="", require_success=True):
    """
    Fetches the given URL, using the parameters provided.
    
    Any data will automatically be encoded and escaped.  Data can be in the form
    of a dictionary or a character string.  Supplying any data will make the
    request use the POST method, otherwise the GET method will be used.  The
    type of method used can be forced by supplying a method parameter.  If data
    is sent using the GET method, then it will be encoded and appended to the
    URL.
    
    A standard Django HttpResponse will be returned.  If require_success is
    True (the default), then a non-okay status code will result in a HttpError
    being thrown.  Setting this to False will result in the error being returned
    encoded as a HttpResponse.   
    """
    # Encode the data.
    if isinstance(data, basestring):
        data = urllib.quote_plus(data)
    else:
        data = urllib.urlencode(data, doseq=True)
    # Allow GET requests to be forced.
    if method == GET and data:
        url += "?" + data
        data = ""
    elif method == POST and not data:
        raise ValueError, "Cannot send a POST request with no data."
    # Create the request.
    request = urllib2.Request(url, data, headers)
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
    
    
def open_xml(*args, **kwargs):
    """Fetches an XML document, returning an XML object."""
    response = open(*args, **kwargs)
    return xml.parse(response.content)
    
    