"""Custom middleware used by the pages application."""


from __future__ import with_statement

import sys

from django.conf import settings
from django.core import urlresolvers
from django.core.handlers.base import BaseHandler
from django.http import Http404, HttpResponse
from django.views.debug import technical_404_response
from django.shortcuts import redirect

from cms.apps.pages.models import Page, cache, publication_manager


REQUEST_PAGE_CACHE_ATTRIBUTE = "_page_cache"


class LazyPage(object):
    
    """Lazily loads the current page."""
    
    def __get__(self, request, obj_type=None):
        """Loads the page on first attribute access."""
        if not hasattr(request, REQUEST_PAGE_CACHE_ATTRIBUTE):
            try:
                page = Page.objects.get_by_path(request.path)
            except Page.DoesNotExist:
                page = None
            setattr(request, REQUEST_PAGE_CACHE_ATTRIBUTE, page)
        return getattr(request, REQUEST_PAGE_CACHE_ATTRIBUTE)


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
        # Add the lazy page loader to the request. Modifying the request's class
        # seems very dodgy to me, but that's how Django's lazy user loading
        # works, so who am I to argue?
        request.__class__.page = LazyPage()
        # See if preview mode is requested.
        try:
            preview_mode = int(request.GET.get(settings.PUBLICATION_PREVIEW_KEY, 0))
        except ValueError:
            preview_mode = False
        # Only allow preview mode if the user is a logged in administrator.
        preview_mode = preview_mode and request.user.is_authenticated() and request.user.is_staff and request.user.is_active
        with publication_manager.select_published(not preview_mode):
            resolver = urlresolvers.get_resolver(None)
            try:
                # Try to match the given path with the URL conf. If it fails, then
                # attempt to dispatch to a page.
                resolver.resolve(request.path)
            except urlresolvers.Resolver404:
                page = request.page
                script_name = page.get_absolute_url()[:-1]
                path_info = request.path[len(script_name):]
                # Append a slash to match the page precisely.
                if not path_info and not request.path.endswith("/") and settings.APPEND_SLASH:
                    return redirect(request.path + "/")
                # Dispatch to the content.
                try:
                    content = page.content
                    try:
                        callback, callback_args, callback_kwargs = urlresolvers.resolve(path_info, content.urlconf)
                    except urlresolvers.Resolver404:
                        # First of all see if adding a slash will help matters.
                        if settings.APPEND_SLASH:
                            new_path_info = path_info + "/"
                            try:
                                urlresolvers.resolve(new_path_info, content.urlconf)
                            except urlresolvers.Resolver404:
                                pass
                            else:
                                return redirect(script_name + new_path_info)
                        raise Http404, "No match for the current path '%s' found in the url conf of %s." % (path_info, content.__class__.__name__)
                    response = callback(request, *callback_args, **callback_kwargs)
                    # Validate the response.
                    if not isinstance(response, HttpResponse):
                        raise ValueError, "The view %s.%s didn't return an HttpResponse object." % (self.__class__.__name__, callback.__name__)
                    return response
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
        
        