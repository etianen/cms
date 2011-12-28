"""Custom middleware used by the pages application."""


from __future__ import with_statement

import sys

from django.conf import settings
from django.core import urlresolvers
from django.core.handlers.base import BaseHandler
from django.http import Http404
from django.views.debug import technical_404_response
from django.shortcuts import redirect

from cms.models import publication_manager, PublicationManagementError
from cms.pages import get_backend


class PreviewMiddleware(object):
    
    """Middleware that enables preview mode for admin users."""
    
    def process_request(self, request):
        """Starts preview mode, if available."""
        # See if preview mode is requested.
        try:
            preview_mode = int(request.GET.get("preview", 0))
        except ValueError:
            preview_mode = False
        # Only allow preview mode if the user is a logged in administrator.
        preview_mode = preview_mode and request.user.is_authenticated() and request.user.is_staff and request.user.is_active
        publication_manager.begin(not preview_mode)
        
    def process_response(self, request, response):
        """Cleans up after preview mode."""
        # Clean up all blocks.
        while True:
            try:
                publication_manager.end()
            except PublicationManagementError:
                break
        # Carry on as normal.
        return response


class PageMiddleware(object):
    
    """Serves up pages when no other view is matched."""
    
    def __init__(self):
        """Initializes the PageMiddleware."""
        self.backend = get_backend()
    
    def process_request(self, request):
        """Annotates the request with a page backend."""
        # Mount the page backend.
        self.backend.mount(request)
            
    def process_response(self, request, response):
        """If the response was a 404, attempt to serve up a page."""
        if response.status_code != 404:
            return response
        # Get the current page.
        page = request.pages.current
        if page is None:
            return response
        script_name = page.get_absolute_url()[:-1]
        path_info = request.path[len(script_name):]
        # Dispatch to the content.
        try:
            try:
                callback, callback_args, callback_kwargs = self.backend.resolve(request, page, path_info)
            except urlresolvers.Resolver404:
                # First of all see if adding a slash will help matters.
                if settings.APPEND_SLASH:
                    new_path_info = path_info + "/"
                    try:
                        self.backend.resolve(request, page, new_path_info)
                    except urlresolvers.Resolver404:
                        pass
                    else:
                        return redirect(script_name + new_path_info)
                return response
            response = callback(request, *callback_args, **callback_kwargs)
            # Validate the response.
            if not response:
                raise ValueError, "The view {0!r} didn't return an HttpResponse object.".format(callback.__name__)
            return response.render()
        except Http404, ex:
            if settings.DEBUG:
                return technical_404_response(request, ex)
            # Let the normal 404 mechanisms render an error page.
            return response
        except:
            return BaseHandler().handle_uncaught_exception(request, urlresolvers.get_resolver(), sys.exc_info())