"""Simple library for fetching remote URLs."""


import urllib, urllib2

from django.http import HttpResponse

from cms.apps.utils import xml


def fetch(url, post_data={}, get_data={}, headers={}, username="", password="", require_success=True, timeout=None):
    """
    Fetches the given URL, using the parameters provided.
    
    Any get data will automatically be encoded and appended to the URL.
    
    A standard Django HttpResponse will be returned.  If require_success is
    True (the default), then a non 200 status code will result in an error being
    thrown.  Setting this to False will result in the error being returned
    encoded as a HttpResponse.   
    """
    # Encode the query string, if any.
    if get_data:
        if "?" in url:
            url += "&"
        else:
            url += "?"
        query_string = urllib.urlencode(get_data)
        url += query_string
    # Create the request.
    request = urllib2.Request(url, post_data, headers)
    # Create an opener.
    opener = urllib2.build_opener()
    # Create an authentication handler.
    if username:
        password_manager = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_manager.add_password(None, url, username, password)
        opener.add_handler(password_manager)
    try:
        # Fetch the response.
        response_content = opener.open(request, timeout=timeout)
    except urllib2.HTTPError, ex:
        # Made a connection, but the server was not happy.
        if require_success:
            raise
        response_content = ex
    except urllib2.URLError:
        # No network connection - go nuts!
        raise
    else:
        status = 200
    # Parse the response.
    response = HttpResponse(response_content, status=status)
    for key, value in response_content.info().items():
        response[key] = value
    return response
    
    
def fetch_xml(*args, **kwargs):
    """Fetches an XML document, returning an XML object."""
    response = fetch(*args, **kwargs)
    return xml.parse(response.content)
    
    