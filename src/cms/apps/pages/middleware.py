"""Custom middleware used by the pages application."""

import sys

from django.conf import settings
from django.core import urlresolvers
from django.core.handlers.base import BaseHandler
from django.http import Http404
from django.views.debug import technical_404_response
from django.shortcuts import redirect
from django.utils.functional import cached_property
from django.template.response import SimpleTemplateResponse

from cms.apps.pages.models import Page


class RequestPageManager(object):
    
    """Handles loading page objects."""
    
    def __init__(self, path, path_info):
        """Initializes the RequestPageManager."""
        self._path = path
        self._path_info = path_info
        
    @cached_property
    def homepage(self):
        """Returns the site homepage."""
        try:
            return Page.objects.get_homepage()
        except Page.DoesNotExist:
            return None
        
    @property
    def is_homepage(self):
        """Whether the current request is for the site homepage."""
        return self._path == self.homepage.get_absolute_url()
    
    @cached_property
    def breadcrumbs(self):
        """The breadcrumbs for the current request."""
        breadcrumbs = []
        slugs = self._path_info.strip("/").split("/")
        slugs.reverse()
        def do_breadcrumbs(page):
            breadcrumbs.append(page)
            if slugs:
                slug = slugs.pop()
                for child in page.children:
                    if child.url_title == slug:
                        do_breadcrumbs(child)
                        break
        if self.homepage:
            do_breadcrumbs(self.homepage)
        return breadcrumbs
    
    @property
    def section(self):
        """The current primary level section, or None."""
        try:
            return self.breadcrumbs[1]
        except IndexError:
            return None
        
    @property
    def subsection(self):
        """The current secondary level section, or None."""
        try:
            return self.breadcrumbs[2]
        except IndexError:
            return None
    
    @property
    def current(self):
        """The current best-matched page."""
        try:
            return self.breadcrumbs[-1]
        except IndexError:
            return None
        
    @property
    def is_exact(self):
        """Whether the current page exactly matches the request URL."""
        return self.current.get_absolute_url() == self._path


class PageMiddleware(object):
    
    """Serves up pages when no other view is matched."""
    
    def process_request(self, request):
        """Annotates the request with a page manager."""
        request.pages = RequestPageManager(request.path, request.path_info)
            
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
                callback, callback_args, callback_kwargs = urlresolvers.resolve(path_info, page.content.urlconf)
            except urlresolvers.Resolver404:
                # First of all see if adding a slash will help matters.
                if settings.APPEND_SLASH:
                    new_path_info = path_info + "/"
                    try:
                        urlresolvers.resolve(new_path_info, page.content.urlconf)
                    except urlresolvers.Resolver404:
                        pass
                    else:
                        return redirect(script_name + new_path_info)
                return response
            response = callback(request, *callback_args, **callback_kwargs)
            # Validate the response.
            if not response:
                raise ValueError, "The view {0!r} didn't return an HttpResponse object.".format(callback.__name__)
            if isinstance(response, SimpleTemplateResponse):
                return response.render()
            return response
        except Http404, ex:
            if settings.DEBUG:
                return technical_404_response(request, ex)
            # Let the normal 404 mechanisms render an error page.
            return response
        except:
            return BaseHandler().handle_uncaught_exception(request, urlresolvers.get_resolver(None), sys.exc_info())