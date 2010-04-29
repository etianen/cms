"""Management routines used by the CMS."""


from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_syncdb

from cms.apps.pages.models import Page
from cms.apps.pages import content


def create_content_permissions(**kwargs):
    """Creates all permissions for registered content models."""
    content_type = ContentType.objects.get_for_model(Page)
    for slug, content_cls in content.registered_content.items():
        if content_cls == content.DefaultContent:
            continue
        name = u"Can add %s page" % content_cls.verbose_name
        codename = content.get_add_permission(slug)
        Permission.objects.get_or_create(content_type=content_type,
                                         codename=codename,
                                         defaults={"name": name})


post_syncdb.connect(create_content_permissions)