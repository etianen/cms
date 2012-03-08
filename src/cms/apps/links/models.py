""""Content used by the links application."""

from django.db import models

from cms.apps.pages.models import ContentBase


class Link(ContentBase):
    
    """A redirect to another URL."""
    
    classifier = "utilities"
    
    icon = "links/img/link.png"
    
    urlconf = "cms.apps.links.urls"
    
    link_url = models.CharField(
        "link URL",
        max_length = 1000,
        help_text = "The URL where the user will be redirected.",
    )
    
