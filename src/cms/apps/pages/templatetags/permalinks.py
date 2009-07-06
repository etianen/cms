"""Permalink processing template tags."""


import re

from django import template
from django.core.exceptions import ObjectDoesNotExist

from cms.apps.pages import permalinks
from cms.apps.pages.models import Page
from cms.apps.pages.templatetags import Library


register = Library()


@register.filter
def permalink(obj):
    """Generates a permalink for the given object."""
    return permalinks.create(obj)


RE_ANCHOR = re.compile(r"""<a.*?\shref=["'](.+?)["'].*?>""", re.IGNORECASE)


@register.filter
def expand_permalinks(text):
    """
    Expands all the permalinks found in anchor tags in the given HTML text.
    """
    offset = 0
    for match in RE_ANCHOR.finditer(text):
        href = match.group(1)
        # Try to match a generic permalink.
        try:
            obj = permalinks.resolve(href)
        except permalinks.PermalinkError:
            # Not a permalink... try to match a page permalink.
            try:
                obj = Page.objects.get_page(href)
            except Page.DoesNotExist:
                continue
        except ObjectDoesNotExist:
            continue
        new_href = obj.get_absolute_url()
        # Substitute in the new href.
        start = match.start(1)
        end = match.end(1)
        text = u"".join((text[:start+offset], new_href, text[end+offset:]))
        offset += len(new_href) - len(href)
    return text

