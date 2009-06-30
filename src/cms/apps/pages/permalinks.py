"""
Generic permalink generation utilities.

A permalink is a model and object id encoded into a URL.  It allows the model to
change it's absolute URL without breaking links.
"""


from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse, resolve as resolve_url, Resolver404

from cms.apps.pages.views import permalink_redirect


class PermalinkError(Exception):
    
    """Exception thrown when an error occurs with a permalink."""


def create(obj):
    """Generates a permalink for the given object."""
    content_type = ContentType.objects.get_for_model(obj)
    content_type_id = content_type.id
    object_id = obj.pk
    kwargs = {"content_type_id": content_type_id,
              "object_id": object_id}
    return reverse("permalink_redirect", kwargs=kwargs)
    
    
def resolve(url):
    """
    Resolves the given permalink into an object.
    
    Raises a PermalinkError if the URL is not a valid permalink.  Raises an
    ObjectDoesNotExist if the referenced object does not exist.
    """
    # Attempt to resolve the URL.
    try:
        callback, callback_args, callback_kwargs = resolve_url(url)
    except Resolver404:
        raise PermalinkError, "'%s' is not a recognised URL in this site." % url
    # Check if the URL refers to a permalink.
    if callback != permalink_redirect:
        raise PermalinkError, "'%s' is not a valid permalink." % url
    # Get the permalink attributes.
    try:
        content_type_id = callback_kwargs["content_type_id"]
        object_id = callback_kwargs["object_id"]
    except IndexError:
        raise ImproperlyConfigured, "The permalink_redirect view should be configured using keywork arguments."
    # Resolve the object. 
    content_type = ContentType.objects.get_for_id(content_type_id)
    obj = content_type.get_object_for_this_type(id=object_id)
    return obj

