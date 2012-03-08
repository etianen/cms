"""Custom middleware used by the pages application."""

from cms.models import publication_manager, PublicationManagementError


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