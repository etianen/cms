"""Registration helpers."""

from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType

from cms.apps.permalinks.models import Permalink


_registry = set()


def save_permalink(instance, **kwargs):
    """Saves a permalink for models with a get_absolute_url method."""
    Permalink.objects.create_for_obj(instance)


class PermalinkRegistrationError(Exception):
    
    """Something went wrong with permalink registration."""


def is_registered(model):
    """Checks whether the given model is registered with the permalinks service."""
    return model in _registry


def get_registered_models():
    """Returns all models that have been registered with the permalinks service."""
    return _registry


def register(model):
    """Registers the model with the permalinks service."""
    if is_registered(model):
        raise PermalinkRegistrationError("{0!r} is already registered with the permalinks service.".format(model.__name__))
    post_save.connect(save_permalink, sender=model)
    _registry.add(model)
    
    
def unregister(model):
    """Unregisters the model with the permalinks service."""
    if not is_registered(model):
        raise PermalinkRegistrationError("{0!r} is not registered with the permalinks service.".format(model.__name__))
    post_save.disconnect(save_permalink, sender=model)
    _registry.remove(model)