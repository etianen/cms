"""Template tags used by the permalink utilities."""


from django import template

from cms.pages import permalinks


register = template.Library()


@register.filter
def permalink(obj):
    """Generates a permalink for the given object."""
    return permalinks.create(obj)

