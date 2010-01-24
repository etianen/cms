"""Template tags for rendering pagination."""


from django import template
from django.conf import settings
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404

from cms.apps.pages.templatetags import PatternNode


register = template.Library()


@register.tag
def paginate(parser, token):
    """Paginates the given queryset as sets it in the context as a variable."""
    def handler(context, queryset, varname, page_size=10):
        request = context["request"]
        # Parse the page number.
        try:
            page_number = int(request.GET[settings.PAGINATION_KEY])
        except (KeyError, TypeError, ValueError):
            page_number = 1
        # Create the paginator.
        try:
            page = Paginator(queryset, page_size).page(page_number)
        except InvalidPage:
            raise Http404, "There are no items on page %s." % page_number
        # Set the context variable.
        context[varname] = page
        return ""
    return PatternNode(parser, token, handler, ("{queryset} into {page_size} as [varname]", "{queryset} as [varname]",))

