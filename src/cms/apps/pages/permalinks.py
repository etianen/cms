"""
Generic permalink generation utilities.

A permalink is a model and object id encoded into a URL.  It allows the model to
change it's absolute URL without breaking links.
"""


from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse


def create(obj):
    """Generates a permalink for the given object."""
    content_type = ContentType.objects.get_for_model(obj)
    content_type_id = content_type.id
    object_id = obj.pk
    return reverse("permalink_redirect", args=(content_type_id, object_id))
    
    