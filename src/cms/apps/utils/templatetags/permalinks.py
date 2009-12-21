"""Permalink processing template tags."""


import re

from django.core.exceptions import ObjectDoesNotExist
from django.forms.fields import slug_re

from cms.apps.pages.models import Page
from cms.apps.pages.templatetags import Library
from cms.apps.utils import permalinks


register = Library()


@register.filter
def permalink(obj):
    """Generates a permalink for the given object."""
    return permalinks.create(obj)


RE_ANCHOR = re.compile(ur"""(<a.*?\shref=["'])(.+?)(["'].*?>)""", re.IGNORECASE)


@register.filter
def expand_permalinks(text):
    """
    Expands all the permalinks found in anchor tags in the given HTML text.
    """
    def replacement(match):
        href = match.group(2)
        obj = None
        # Try to match a generic permalink.
        try:
            obj = permalinks.resolve(href)
        except permalinks.PermalinkError:
            pass
        except ObjectDoesNotExist:
            pass
        # Try to match a page permalink.
        if obj is None and slug_re.search(href):
            try:
                obj = Page.objects.get_page(href)
            except Page.DoesNotExist:
                pass
        # If an object was found, substitute it's href.
        if obj is not None:
            try:
                href = obj.get_absolute_url()
            except AttributeError:
                pass
        return u"".join((match.group(1), href, match.group(3)))
    return RE_ANCHOR.sub(replacement, text)

