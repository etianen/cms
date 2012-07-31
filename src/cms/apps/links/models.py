""""Content used by the links application."""

from cms.models import LinkField
from cms.apps.pages.models import ContentBase


class Link(ContentBase):
    
    """A redirect to another URL."""
    
    classifier = "utilities"
    
    icon = "links/img/link.png"
    
    urlconf = "cms.apps.links.urls"
    
    robots_index = False
    
    link_url = LinkField(
        "link URL",
        help_text = "The URL where the user will be redirected.",
    )