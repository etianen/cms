""""Content used by the redirects application."""


from django.conf import settings
from django.http import HttpResponseRedirect

from cms.apps.pages import content


class Redirect(content.ContentBase):
    
    """A redirect to another URL."""
    
    classifier = "utilities"
    
    icon = settings.CMS_MEDIA_URL + "img/content-types/redirect.png"
    
    redirect_url = content.CharField("redirect URL",
                                     required=True,
                                     help_text="The URL where the user will be redirected.")
    
    @content.view(r"^$")
    def index(self, request):
        """Redirects to the redirect URL."""
        redirect_url = self.redirect_url
        return HttpResponseRedirect(redirect_url)
    
        
content.register(Redirect)

