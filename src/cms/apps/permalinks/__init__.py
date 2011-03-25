"""Permalink services."""

from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType

from cms.apps.permalinks.models import Permalink


def save_permalink(instance, **kwargs):
    """Saves a permalink for models with a get_absolute_url method."""
    Permalink.objects.create_for_obj(instance)


def register(model):
    """Registers the model with the permalinks service."""
    post_save.connect(save_permalink, sender=model)
    
    
def unregister(model):
    """Unregisters the model with the permalinks service."""
    post_save.disconnect(save_permalink, sender=model)