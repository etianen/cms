"""Permalink generation template tags."""


from django import template
from django.utils.html import escape

from cms import permalinks


register = template.Library()


@register.filter
def permalink(model):
    """Returns a permalink for the given model."""
    return permalinks.create(model)


@register.simple_tag(takes_context=True)
def permalink_absolute(context, model):
    request = context["request"]
    return escape(request.build_absolute_uri(permalinks.create(model)))