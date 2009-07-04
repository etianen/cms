"""Custom middleware used by the pages application."""


import sys

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.views.debug import technical_404_response, technical_500_response

from cms.apps.pages.models import Page, cache


class PageMiddleware(object):
    
    """Serves up pages when no other view is matched."""
    
    def not_found_response(self, request, page):
        """Renders a pretty not found page."""
        context = {"title": "Page Not Found"}
        response = page.content.render_to_response(request, "404.html", context)
        response.status_code = 404
        return response
    
    def error_response(self, request, page):
        """Renders a pretty error page."""
        context = {"title": "Server Error"}
        response = page.content.render_to_response(request, "500.html", context)
        response.status_code = 500
        return response
    
    def process_response(self, request, response):
        """Falls back to page dispatch."""
        try:
            # If the urlconf matched the request with no error, then ignore.
            if response.status_code not in (404, 500):
                return response
            # See if we have pages to dispatch to.
            try:
                page = Page.objects.get_homepage()
            except PageDoesNotExist:
                return response
            # Get the most exact page match.
            breadcrumbs = [page]
            try:
                for slug in request.path.strip("/").split("/"):
                    page = page.children.get(url_title=slug)
                    breadcrumbs.append(page)
            except Page.DoesNotExist:
                pass
            # Handle server errors.
            if response.status_code == 500:
                if settings.DEBUG:
                    return response
                return self.error_response(request, page)
            # Try to dispatch to a page.
            path_info = request.path[len(page.url):]
            # Append a slash to match the page precisely.
            if not path_info and not request.path.endswith("/") and settings.APPEND_SLASH:
                return HttpResponseRedirect(request.path + "/")
            # Dispatch to the content.
            try:
                return page.content.dispatch(request, path_info)
            except Http404, ex:
                if settings.DEBUG:
                    return technical_404_response(request, ex)
                return self.not_found_response(request, page)
            except:
                if settings.DEBUG:
                    return technical_500_response(request, *sys.exc_info())
                return self.error_response(request, page)
        finally:
            cache.clear()
            
    