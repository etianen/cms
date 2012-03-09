"""Permalink generation template tags."""


from django import template
from django.utils.html import escape

from optimizations.templatetags import simple_tag

from cms.core import permalinks


register = template.Library()


@register.filter
def permalink(model):
    """Returns a permalink for the given model."""
    return permalinks.create(model)



@simple_tag(register, takes_context=True)
def permalink_absolute(context, model):
    request = context["request"]
    return escape(request.build_absolute_uri(permalinks.create(model)))
