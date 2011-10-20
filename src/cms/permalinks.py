"""
Generic permalink generation utilities.

A permalink is a model and object id encoded into a URL.  It allows the model to
change it's absolute URL without breaking links.
"""


from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.views import shortcut
from django.core import urlresolvers
from django.core.exceptions import ImproperlyConfigured


__all__ = ("PermalinkError", "create", "resolve", "expand",)


class PermalinkError(Exception):
    
    """Exception thrown when an error occurs with a permalink."""


def create(obj):
    """Generates a permalink for the given object."""
    content_type = ContentType.objects.get_for_model(obj)
    content_type_id = content_type.id
    object_id = obj.pk
    kwargs = {"content_type_id": content_type_id,
              "object_id": object_id}
    return urlresolvers.reverse("permalink_redirect", kwargs=kwargs)
    
    
def resolve(permalink):
    """
    Resolves the given permalink into an object.
    
    Raises a PermalinkError if the URL is not a valid permalink. Raises an
    ObjectDoesNotExist if the referenced object does not exist.
    """
    # Attempt to resolve the URL.
    try:
        callback, _, callback_kwargs = urlresolvers.resolve(permalink)  # @UnusedVariable
    except (urlresolvers.Resolver404, TypeError):
        raise PermalinkError, "'%s' is not a valid permalink." % permalink
    # Check if the URL refers to a permalink.
    if callback != shortcut:
        raise PermalinkError, "'%s' is not a valid permalink." % permalink
    # Get the permalink attributes.
    try:
        content_type_id = callback_kwargs["content_type_id"]
        object_id = callback_kwargs["object_id"]
    except KeyError:
        raise ImproperlyConfigured, "The permalink_redirect view should be configured using keyword arguments."
    # Resolve the object. 
    content_type = ContentType.objects.get_for_id(content_type_id)
    obj = content_type.get_object_for_this_type(id=object_id)
    return obj


def expand(permalink):
    """
    Expands the given permalink into a full URL.
    
    Raises a permalink error if the URL is not a valid permalink. Raises an
    ObjectDoesNotExist if the referenced object does not exist.
    """
    obj = resolve(permalink)
    return obj.get_absolute_url()
    
    