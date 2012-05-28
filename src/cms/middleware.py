"""Custom middleware used by the pages application."""

import re

from django.conf import settings
from django.template.response import SimpleTemplateResponse

from cms.models import publication_manager, PublicationManagementError


class PublicationMiddleware(object):
    
    """Middleware that enables preview mode for admin users."""
    
    def __init__(self):
        """Initializes the PublicationMiddleware."""
        self.exclude_urls = [
            re.compile(url)
            for url in
            getattr(settings, "PUBLICATION_MIDDLEWARE_EXCLUDE_URLS", ())
        ]
    
    def process_request(self, request):
        """Starts preview mode, if available."""
        if not any(pattern.match(request.path_info[1:]) for pattern in self.exclude_urls):
            # See if preview mode is requested.
            try:
                preview_mode = bool(int(request.GET.get("preview", 0)))
            except ValueError:
                preview_mode = False
            # Only allow preview mode if the user is a logged in administrator.
            preview_mode = preview_mode and request.user.is_authenticated() and request.user.is_staff and request.user.is_active
            publication_manager.begin(not preview_mode)
        
    def process_response(self, request, response):
        """Cleans up after preview mode."""
        # Render the response if we're in a block of publication management.
        if publication_manager.select_published_active():
            if isinstance(response, SimpleTemplateResponse):
                response = response.render()
        # Clean up all blocks.
        while True:
            try:
                publication_manager.end()
            except PublicationManagementError:
                break
        # Carry on as normal.
        return response