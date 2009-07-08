"""Template tags used to generate pagination."""


import urllib

from django import template
from django.conf import settings

from cms.apps.pages.templatetags import Library


register = Library()


@register.inclusion_tag("pagination.html", takes_context=True)
def pagination(context, page):
    """Generates pagination for the given page."""
    request = context["request"]
    paginator = page.paginator
    # Generate the context.
    context = {"request": request,
               "count": paginator.count,
               "num_pages": paginator.num_pages,
               "page_range": paginator.page_range,
               "has_next": page.has_next(),
               "has_previous": page.has_previous(),
               "has_other_pages": page.has_other_pages(),
               "page_number": page.number,
               "next_page_number":page.next_page_number(),
               "previous_page_number": page.previous_page_number(),
               "start_index": page.start_index(),
               "end_index": page.end_index()}
    return context


@register.context_tag
def pagination_url(context, page_number, pagination_key=None):
    """Generates a link to the given page number in the pagination."""
    request = context["request"]
    pagination_key = pagination_key or settings.PAGINATION_KEY
    get_params = request.GET.copy()
    get_params[pagination_key] = page_number
    query_string = urllib.urlencode(get_params)
    url = request.path + "?" + query_string
    return url

