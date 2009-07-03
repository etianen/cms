"""Site-based utilities."""


from django.conf import settings
from django.contrib.sites.models import Site


def add_domain(url):
    """Adds the current domain to the URL, if not present."""
    if not url.startswith("http:") and not url.startswith("https:/"):
        domain = settings.site.domain
        url = "http://%s%s" % (site.domain, url)
    return url

