""""Content used by the links application."""


from django.conf import settings

from cms.apps.pages import content


class Redirect(content.ContentBase):
    
    """A redirect to another URL."""
    
    classifier = "utilities"
    
    icon = settings.CMS_MEDIA_URL + "img/content-types/redirect.png"
    
    urlconf = "cms.apps.links.urls"
    
    redirect_url = content.CharField("redirect URL",
                                     help_text="The URL where the user will be redirected.  You can also enter a page permalink to create a dynamic link to a page.")
    
