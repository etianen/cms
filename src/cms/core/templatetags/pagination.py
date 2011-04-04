"""Template tags for rendering pagination."""


from django import template
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
from django.utils.html import escape

from cms.core.templatetags import PatternNode


register = template.Library()


@register.tag
def paginate(parser, token):
    """Paginates the given queryset as sets it in the context as a variable."""
    def handler(context, queryset, varname, page_size=10, pagination_key="page"):
        request = context["request"]
        # Parse the page number.
        try:
            page_number = int(request.GET[pagination_key])
        except (KeyError, TypeError, ValueError):
            page_number = 1
        # Create the paginator.
        try:
            page = Paginator(queryset, page_size).page(page_number)
        except InvalidPage:
            raise Http404, "There are no items on page %s." % page_number
        page._pagination_key = pagination_key
        # Set the context variable.
        context[varname] = page
        return ""
    return PatternNode(parser, token, handler, (
        "{queryset} into {page_size} as [varname] using [pagination_key]",
        "{queryset} into {page_size} as [varname]",
        "{queryset} as [varname] using [pagination_key]",
        "{queryset} as [varname]",
    ))


@register.simple_tag(takes_context=True)
def pagination(context, page_obj):
    """Renders the pagination for the given page of items."""
    context.push()
    try:
        context.update({
            "page_obj": page_obj,
            "paginator": page_obj.paginator,
            "pagination_key": getattr(page_obj, "_pagination_key", "page")
        })
        return template.loader.render_to_string("pagination.html", context)
    finally:
        context.pop()


@register.simple_tag(takes_context=True)
def pagination_url(context, page_number):
    """Renders the URL for the given page number."""
    request = context["request"]
    params = request.GET.copy()
    params[context["pagination_key"]] = page_number
    url = "?%s" % params.urlencode()
    return escape(url)