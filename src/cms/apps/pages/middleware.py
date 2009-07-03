"""Custom middleware used by the pages application."""


import sys

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.views.debug import technical_404_response, technical_500_response

from cms.apps.pages.models import Page


class PageMiddleware(object):
    
    """Serves up pages when no other view is matched."""
    
    def process_request(self, request):
        """Adds the breadcrumbs to the request."""
        slugs = request.path.strip("/").split("/")
        breadcrumbs = []
        request.breadcrumbs = breadcrumbs
        try:
            page = Page.objects.get_homepage()
            breadcrumbs.append(page)
            for slug in slugs:
                page = page.children.get(url_title=slug)
                breadcrumbs.append(page)
        except Page.DoesNotExist:
            return
        
    def process_response(self, request, response):
        """Falls back to page dispatch."""
        # If no breadcrumbs, ignore.
        breadcrumbs = getattr(request, "breadcrumbs", [])
        if not breadcrumbs:
            return response
        # If the urlconf matched the request, then ignore.
        if response.status_code != 404:
            return response
        # Try to dispatch to a page.
        page = breadcrumbs[-1]
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
            context = {"title": "Page Not Found"}
            response = page.content.render_to_response(request, "404.html", context)
            response.status_code = 404
            return response
        except:
            if settings.DEBUG:
                return technical_500_response(request, *sys.exc_info())
            context = {"title": "Server Error"}
            response = page.content.render_to_response(request, "500.html", context)
            response.status_code = 500
            return response
    