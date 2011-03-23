"""Management routines used by the CMS."""

from django.contrib.sites.models import Site
from django.db.models.signals import post_delete


# HACK: For some reason, the sitemaps unit tests are failing due to a polluted cache.
def clear_site_cache_on_delete(**kwargs):
    """Clears the site cache when a site is deleted."""
    Site.objects.clear_cache()

post_delete.connect(clear_site_cache_on_delete)