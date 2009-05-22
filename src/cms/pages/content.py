"""Some base page content types."""


class Content(object):
    
    """
    The base page content type.
    
    Subclasses should extend this with additional functionality.
    """
    
    def __init__(self, page, content_data):
        """Initializes the page content."""
        self.page = page
        self._content_data = content_data
        
        

class SimpleContent(Content):
    
    """A single column content page."""
    
    