"""Template tags for rendering pagination."""


from django import template
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
from django.utils.html import escape

from optimizations.templatetags import parameter_tag, template_tag


register = template.Library()


@parameter_tag(register, takes_context=True)
def paginate(context, queryset, per_page=10, key="page"):
    """Paginates the given queryset as sets it in the context as a variable."""
    request = context["request"]
    # Parse the page number.
    try:
        page_number = int(request.GET[key])
    except (KeyError, TypeError, ValueError):
        page_number = 1
    # Create the paginator.
    try:
        page = Paginator(queryset, per_page).page(page_number)
    except InvalidPage:
        raise Http404, "There are no items on page %s." % page_number
    page._pagination_key = key
    return page


@template_tag(register, "pagination.html")
def pagination(page_obj):
    """Renders the pagination for the given page of items."""
    return {
        "page_obj": page_obj,
        "paginator": page_obj.paginator,
        "pagination_key": getattr(page_obj, "_pagination_key", "page")
    }


@parameter_tag(register, takes_context=True)
def pagination_url(context, page_number):
    """Renders the URL for the given page number."""
    request = context["request"]
    params = request.GET.copy()
    params[context["pagination_key"]] = page_number
    url = "?%s" % params.urlencode()
    return escape(url)