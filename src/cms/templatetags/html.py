"""Template tags used for processing HTML."""

from django import template
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter

from cms.html import process as process_html


register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def html(text):
    """
    Processes HTML text.
    
    The text is checked for permalinks embedded in <a> tags, expanding the
    permalinks to their referenced URL. Images containing a permalink source
    are checked for size and thumbnailed as appropriate.
    """
    if not text:
        return ""
    text = process_html(text)
    return mark_safe(text)


@register.filter(is_safe=True)
@stringfilter
def truncate_paragraphs(text, number):
    """Truncates to the end of the given number of paragraphs in the given text."""
    position = 0
    count = 0
    while count < number and position < len(text):
        position = text.find(u"</p>", position)
        if position == -1:
            position = len(text)
        else:
            position += 4
        count += 1
    return text[:position]