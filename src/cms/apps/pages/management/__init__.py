"""Management routines used by the CMS."""


from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.db import models
from django.db.models.signals import post_syncdb

from cms.apps.pages.models import Page
from cms.apps.pages import content


def create_content_permissions(**kwargs):
    """Creates all permissions for registered content models."""
    content_type = ContentType.objects.get_for_model(Page)
    for slug, content_cls in content.registered_content.items():
        if slug == content.DEFAULT_CONTENT_SLUG:
            continue
        name = u"Can add %s page" % content_cls.verbose_name
        codename = content.get_add_permission(slug)
        permission, created = Permission.objects.get_or_create(content_type=content_type,
                                                               codename=codename,
                                                               defaults={"name": name})
    
post_syncdb.connect(create_content_permissions)


def synchronize_current_site(**kwargs):
    """
    Renames the current site object with the site name and domain name in the
    Django settings file.
    """
    site = Site.objects.get_current()
    site.name = settings.SITE_NAME
    site.domain = settings.SITE_DOMAIN
    site.save()
    
    
post_syncdb.connect(synchronize_current_site)

