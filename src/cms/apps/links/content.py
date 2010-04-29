""""Content used by the links application."""


from django.conf import settings

from cms.apps.pages import content


class Link(content.Content):
    
    """A redirect to another URL."""
    
    classifier = "utilities"
    
    icon = settings.CMS_MEDIA_URL + "img/content-types/redirect.png"
    
    urlconf = "cms.apps.links.urls"
    
    link_url = content.CharField("link URL",
                                 help_text="The URL where the user will be redirected.")
    
