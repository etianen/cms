"""Context processors used by the CMS."""


from django.conf import settings


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

