"""Management routines used by the CMS."""


from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.sites import models as sites_app
from django.contrib.sites.models import Site
from django.contrib.sites.management import create_default_site
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_syncdb


def synchronize_current_site(app, **kwargs):
    """
    Changes the fields of the current site to match those in the Django settings
    file.
    """
    site = Site.objects.get_current()
    site.name = settings.SITE_NAME
    domain = settings.SITE_DOMAIN
    if settings.PREPEND_WWW and not domain.startswith("www."):
        domain = "www." + domain
    site.domain = domain
    site.save()


post_syncdb.connect(synchronize_current_site, sender=sites_app)