"""AJAX utility tag library."""


from django.conf import settings
from django.utils import html
from django.utils import safestring

from cms.apps.pages.templatetags import Library


register = Library()


@register.context_tag
def load_jquery(context):
    """Loads the jQuery javascript library."""
    request = context["request"]
    jquery_url = settings.JQUERY_URL
    if jquery_url.startswith("http://") and request.is_secure():
        jquery_url = "https://" + jquery_url[7:]
    return safestring.mark_safe('<script type="text/javascript" src="%s"/>' % html.escape(jquery_url))
    
    