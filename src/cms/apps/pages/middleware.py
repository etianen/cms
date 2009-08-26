"""Custom middleware used by the pages application."""


from __future__ import with_statement

import sys, traceback

from django.conf import settings
from django.core.mail import mail_admins
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.views.debug import technical_404_response, technical_500_response

from cms.apps.pages.models import Page, cache, publication_manager


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
        with publication_manager.select_published(not publication_manager.preview_mode_active(request)):
            try:
                # If the urlconf matched the request with no error, then ignore.
                if response.status_code not in (404, 500):
                    return response
                # See if we have pages to dispatch to.
                try:
                    page = Page.objects.get_homepage()
                except Page.DoesNotExist:
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
                    # Send an email to the admininistrators.
                    # HACK: This is a copy and paste from the base handler code.
                    subject = "Error (%s IP): %s" % ((request.META.get("REMOTE_ADDR") in settings.INTERNAL_IPS and "internal" or "EXTERNAL"), request.path)
                    try:
                        request_repr = repr(request)
                    except:
                        request_repr = "Request repr() unavailable"
                    formatted_traceback = "\n".join(traceback.format_exception(*sys.exc_info()))
                    message = "%s\n\n%s" % (formatted_traceback, request_repr)
                    mail_admins(subject, message, fail_silently=True)
                    # Return the branded error page.
                    return self.error_response(request, page)
            finally:
                cache.clear()
            
    