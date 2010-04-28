"""Template tags for rendering pagination."""


from django import template
from django.conf import settings
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
from django.utils.html import escape
from django.utils.http import urlencode

from cms.core.templatetags import PatternNode


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


@register.tag
def pagination(parser, token):
    """Renders the pagination for the given page of items."""
    def handler(context, item_page):
        context.push()
        try:
            context.update({"num_pages": item_page.paginator.num_pages,
                            "count": item_page.paginator.count,
                            "page_range": item_page.paginator.page_range,
                            "number": item_page.number,
                            "has_other_pages": item_page.has_other_pages(),
                            "has_next": item_page.has_next(),
                            "has_previous": item_page.has_previous(),
                            "next_page_number": item_page.next_page_number(),
                            "previous_page_number": item_page.previous_page_number(),
                            "start_index": item_page.start_index(),
                            "end_index": item_page.end_index()})
            return template.loader.render_to_string("pagination.html", context)
        finally:
            context.pop()
    return PatternNode(parser, token, handler, ("{item_page}",))


@register.tag
def pagination_url(parser, token):
    """Renders the URL for the given page number."""
    def handler(context, page_number):
        request = context["request"]
        params = request.GET.copy()
        params[settings.PAGINATION_KEY] = page_number
        url = "?%s" % urlencode(params)
        return escape(url)
    return PatternNode(parser, token, handler, ("{page_number}",))

