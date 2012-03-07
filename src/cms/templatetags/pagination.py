"""Template tags for rendering pagination."""


from django import template
from django.core.paginator import Paginator, InvalidPage
from django.http import Http404
from django.utils.html import escape

from optimizations.templatetags import simple_tag, template_tag, assignment_tag


register = template.Library()


@assignment_tag(register, takes_context=True)
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


@simple_tag(register, takes_context=True)
def pagination_url(context, page_number):
    """Renders the URL for the given page number."""
    request = context["request"]
    url = request.path
    params = request.GET.copy()
    if unicode(page_number) != u"1":
        params[context["pagination_key"]] = page_number
    else:
        params.pop(context["pagination_key"], None)
    if params:
        url += "?%s" % params.urlencode()
    return escape(url)