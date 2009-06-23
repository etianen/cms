"""Context processors used by the CMS."""


from django.conf import settings

from cms.apps.pages.templatetags.pages import YES, NO, MAYBE


def site(request):
    """Sets the site name and domain in the template."""
    context = {"SITE_NAME": settings.SITE_NAME,
               "SITE_DOMAIN": settings.SITE_DOMAIN}
    return context


def media(request):
    """Sets up the site and cms media references in the template."""
    context = {"SITE_MEDIA_URL": settings.SITE_MEDIA_URL,
               "CMS_MEDIA_URL": settings.CMS_MEDIA_URL}
    return context


def keywords(request):
    """Sets some keywords in the context."""
    context = {"yes": YES,
               "no": NO,
               "maybe": MAYBE}
    return context

