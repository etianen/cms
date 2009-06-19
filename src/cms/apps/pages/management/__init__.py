"""Management routines used by the CMS."""


from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.signals import post_syncdb

from cms.apps.pages.models import PageBase
from cms.apps.pages import content


def create_content_permissions(**kwargs):
    """Creates all permissions for registered content models."""
    for model in models.get_models():
        if issubclass(model, PageBase):
            content_type = ContentType.objects.get_for_model(model)
            for slug, content_cls in model.content_registry.items():
                if slug == content.DEFAULT_CONTENT_SLUG:
                    continue
                name = u"Can add %s %s" % (content_cls.verbose_name, model._meta.verbose_name)
                codename = content.get_add_permission(slug, model)
                permission, created = Permission.objects.get_or_create(content_type=content_type,
                                                                       codename=codename,
                                                                       defaults={"name": name})
    
post_syncdb.connect(create_content_permissions)

