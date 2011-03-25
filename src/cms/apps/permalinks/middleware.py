"""Middleware used by the permalinks service."""

from django.shortcuts import redirect
from cms.apps.permalinks.models import Permalink


class PermalinkFallbackMiddleware(object):
    
    """Middleware that attempts to rescue 404 responses with a redirect to it's new location."""
    
    def process_response(self, request, response):
        """Attempts to rescue 404 responses."""
        if response.status_code == 404:
            # Try to rescue the response.
            try:
                permalink = Permalink.objects.get(path=request.path)
                return redirect(permalink.object, permanent=True)
            except Permalink.DoesNotExist:
                pass
        return response