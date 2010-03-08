"""Permalink generation template tags."""


from django import template

from cms.apps.pages import permalinks


register = template.Library()


@register.filter
def permalink(model):
    """Returns a permalink for the given model."""
    return permalinks.create(model)

