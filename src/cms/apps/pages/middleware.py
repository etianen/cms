"""Custom middleware used by the pages application."""


from __future__ import with_statement

import sys

from django.conf import settings
from django.core import urlresolvers
from django.core.handlers.base import BaseHandler
from django.http import Http404
from django.views.debug import technical_404_response
from django.shortcuts import redirect

from cms.apps.pages.models import Page, cache, publication_manager


class PageMiddleware(object):
    
    """Serves up pages when no other view is matched."""
    
    def process_request(self, request):
        """
        Attempts a page dispatch.
        
        A page dispatch will be carried out if the URL conf does not contain a
        match. This a different strategy to the flatpages app, as it is assumed
        that most requests will require the page dispatch mechanism. If we
        simply caught 404 responses, then there would be a lot of wasted
        template rendering.
        """
        resolver = urlresolvers.get_resolver(None)
        try:
            # Try to match the given path with the URL conf. If it fails, then
            # attempt to dispatch to a page.
            resolver.resolve(request.path)
        except urlresolvers.Resolver404:
            # See if preview mode is requested.
            try:
                preview_mode = int(request.GET.get(settings.PUBLICATION_PREVIEW_KEY, 0))
            except ValueError:
                preview_mode = False
            # Only allow preview mode if the user is a logged in administrator.
            preview_mode = preview_mode and request.user.is_authenticated() and request.user.is_staff and request.user.is_active
            with publication_manager.select_published(not preview_mode):
                # See if we have pages to dispatch to.
                try:
                    page = Page.objects.get_by_path(request.path)
                except Page.DoesNotExist:
                    return
                path_info = request.path[len(page.url):]
                # Append a slash to match the page precisely.
                if not path_info and not request.path.endswith("/") and settings.APPEND_SLASH:
                    return redirect(request.path + "/")
                # Dispatch to the content.
                try:
                    return page.content.dispatch(request, path_info)
                except Http404, ex:
                    if settings.DEBUG:
                        return technical_404_response(request, ex)
                    # Let the normal 404 mechanisms render an error page.
                    return
                except:
                    return BaseHandler().handle_uncaught_exception(request, resolver, sys.exc_info())
            
    def process_response(self, request, response):
        """Clears the page cache."""
        cache.clear()
        return response
        
        