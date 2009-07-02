"""Template tags used by the CMS."""


import re, urllib

from django import template
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

from cms.apps.pages.models import Page
from cms.apps.pages.templatetags import Library
from cms.apps.pages.templatetags.permalinks import expand_permalinks
from cms.apps.pages.templatetags.thumbnails import generate_thumbnails


register = Library()


# HTML processing.


@register.filter
def html(text):
    """
    Processes HTML text.
    
    The text is checked for permalinks embedded in <a> tags, expanding the
    permalinks to their referenced URL.
    """
    if not text:
        return ""
    text = expand_permalinks(text)
    text = generate_thumbnails(text)
    return mark_safe(text)

    
# Page linking.


@register.simple_tag
def page_url(page, view_func="index"):
    """Renders the URL of the given view func in the given page."""
    if isinstance(page, int):
        try:
            page = Page.objects.get(id=page)
        except Page.DoesNotExist:
            return "#"
    return page.content.reverse(view_func)


# Pagination.


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


HERE_CLASS_NAME = "here"


@register.context_tag
def here(context, url):
    """
    Returns 'here' if the url is at the start of the current request path.
    """
    request = context["request"]
    if request.path.startswith(url):
        return HERE_CLASS_NAME
    return ""


@register.context_tag
def here_exact(context, url):
    """
    Returns 'here' if the url is exactly equal to current request path.
    """
    request = context["request"]
    if request.path == url:
        return HERE_CLASS_NAME
    return ""


@register.context_tag
def first(context):
    """Returns 'first' on the first iteration of the parent for loop."""
    if context["forloop"]["first"]:
        return "first"
    return ""


@register.context_tag
def last(context):
    """Returns 'last' on the last iteration of the parent for loop."""
    if context["forloop"]["last"]:
        return "last"
    return ""


@register.body_tag
def repeat(context, nodelist, count):
    """Renders the node."""
    result = []
    if "forloop" in context:
        parentloop = context["forloop"]
    else:
        parentloop = {}
    loop_attrs = {"parentloop": parentloop}
    context.push()
    context["forloop"] = loop_attrs
    try:
        for index in range(count):
            # Update forloop attrs.
            loop_attrs["counter0"] = index
            loop_attrs["counter"] = index + 1
            loop_attrs["revcounter"] = count - index
            loop_attrs["revcounter0"] = count - index - 1
            loop_attrs["first"] = (index == 0)
            loop_attrs["last"] = (index == count - 1)
            result.append(nodelist.render(context))
        return u"".join(result)
    finally:
        context.pop()

    