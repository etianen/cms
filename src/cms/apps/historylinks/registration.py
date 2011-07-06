"""Registration helpers."""

from django.db.models.signals import post_save

from cms.apps.historylinks.models import HistoryLink


_registry = set()


def save_history_link(instance, raw, **kwargs):
    """Saves a link for models with a get_absolute_url method."""
    if not raw:
        HistoryLink.objects.create_for_obj(instance)


class HistoryLinkRegistrationError(Exception):
    
    """Something went wrong with history link registration."""


def is_registered(model):
    """Checks whether the given model is registered with the history links service."""
    return model in _registry


def get_registered_models():
    """Returns all models that have been registered with the history links service."""
    return _registry


def register(model):
    """Registers the model with the history links service."""
    if is_registered(model):
        raise HistoryLinkRegistrationError("{0!r} is already registered with the history links service.".format(model.__name__))
    post_save.connect(save_history_link, sender=model)
    _registry.add(model)
    
    
def unregister(model):
    """Unregisters the model with the history links service."""
    if not is_registered(model):
        raise HistoryLinkRegistrationError("{0!r} is not registered with the history links service.".format(model.__name__))
    post_save.disconnect(save_history_link, sender=model)
    _registry.remove(model)