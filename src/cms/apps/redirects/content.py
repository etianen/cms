""""Content used by the redirects application."""


from django.conf import settings
from django.shortcuts import redirect

from cms.apps.pages import content
from cms.apps.pages.models import Page


class Redirect(content.ContentBase):
    
    """A redirect to another URL."""
    
    classifier = "utilities"
    
    icon = settings.CMS_MEDIA_URL + "img/content-types/redirect.png"
    
    redirect_url = content.CharField("redirect URL",
                                     help_text="The URL where the user will be redirected.  You can also enter a page permalink to create a dynamic link to a page.")
    
    @content.view(r"^$")
    def index(self, request):
        """Redirects to the redirect URL."""
        redirect_url = self.redirect_url
        redirect_url = Page.objects.expand_page_url(redirect_url)
        return redirect(redirect_url)
    
