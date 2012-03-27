"""Custom middleware used by the pages application."""

import sys

from django.conf import settings
from django.core import urlresolvers
from django.core.handlers.base import BaseHandler
from django.db.transaction import commit_on_success
from django.http import Http404, HttpResponse
from django.views.debug import technical_404_response
from django.shortcuts import redirect

from cms.core.models import publication_manager, PublicationManagementError
from cms.core.pages import get_backend


class PreviewMiddleware(object):
    
    """Middleware that enables preview mode for admin users."""
    
    def process_request(self, request):
        """Starts preview mode, if available."""
        # See if preview mode is requested.
        try:
            preview_mode = int(request.GET.get(settings.PUBLICATION_PREVIEW_KEY, 0))
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
        """
        Attempts a page dispatch.
        
        A page dispatch will be carried out if the URL conf does not contain a
        match. This a different strategy to the flatpages app, as it is assumed
        that most requests will require the page dispatch mechanism. If we
        simply caught 404 responses, then there would be a lot of wasted
        template rendering.
        """
        # Mount the page backend.
        self.backend.mount(request)
        # See if the usual resolver will work.
        resolver = urlresolvers.get_resolver(urlresolvers.get_urlconf())
        try:
            # Try to match the given path with the URL conf. If it fails, then
            # attempt to dispatch to a page.
            resolver.resolve(request.path)
        except urlresolvers.Resolver404:
            # Get the current page.
            page = request.pages.current
            if page is None:
                return None
            script_name = page.get_absolute_url()[:-1]
            path_info = request.path[len(script_name):]
            # Append a slash to match the page precisely.
            if not path_info and not request.path.endswith("/") and settings.APPEND_SLASH:
                return redirect(request.path + "/")
            # Dispatch to the content.
            try:
                try:
                    callback, callback_args, callback_kwargs = self.backend.resolve(request, page, path_info)
                except urlresolvers.Resolver404:
                    # First of all see if adding a slash will help matters.
                    if settings.APPEND_SLASH:
                        new_path_info = path_info + "/"
                        try:
                            self.backend.resolve(request, page, path_info)
                        except urlresolvers.Resolver404:
                            pass
                        else:
                            return redirect(script_name + new_path_info)
                    return
                response = commit_on_success(callback)(request, *callback_args, **callback_kwargs)
                # Validate the response.
                if not isinstance(response, HttpResponse):
                    raise ValueError, "The view {0!r} didn't return an HttpResponse object.".format(callback.__name__)
                return response
            except Http404, ex:
                if settings.DEBUG:
                    return technical_404_response(request, ex)
                # Let the normal 404 mechanisms render an error page.
                return
            except:
                return BaseHandler().handle_uncaught_exception(request, resolver, sys.exc_info())