"""Site-based utilities."""


from django.conf import settings


def add_domain(url):
    """Adds the current domain to the URL, if not present."""
    if not url.startswith("http:") and not url.startswith("https:/"):
        domain = settings.SITE_DOMAIN
        if settings.PREPEND_WWW and not domain.startswith("www."):
            domain = "www." + domain
        url = "http://%s%s" % (domain, url)
    return url

