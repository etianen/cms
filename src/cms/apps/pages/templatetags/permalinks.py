"""Permalink processing template tags."""


import re

from django import template
from django.core.exceptions import ObjectDoesNotExist

from cms.apps.pages.models import Page
from cms.apps.pages import permalinks


register = template.Library()


@register.filter
def permalink(obj):
    """Generates a permalink for the given object."""
    return permalinks.create(obj)


RE_ANCHOR = re.compile(ur"""(<a.*?\shref=["'])(.+?)(["'].*?>)""", re.IGNORECASE)


def replace_permalink(match):
    """Replaces the permalink found by the given match object."""
    href = match.group(2)
    obj = None
    # Try to match a generic permalink.
    try:
        obj = permalinks.resolve(href)
    except permalinks.PermalinkError:
        # Try to match a page permalink.
        href = Page.objects.expand_page_url(href)
    except ObjectDoesNotExist:
        pass
    else:
        # If an object was found, substitute it's href.
        if obj is not None:
            try:
                href = obj.get_absolute_url()
            except AttributeError:
                pass
    return u"".join((match.group(1), href, match.group(3)))


@register.filter
def expand_permalinks(text):
    """
    Expands all the permalinks found in anchor tags in the given HTML text.
    """
    return RE_ANCHOR.sub(replace_permalink, text)

