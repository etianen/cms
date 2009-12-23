"""Template tags used by the CMS."""


from django.utils.safestring import mark_safe

from cms.apps.pages.models import Page
from cms.apps.pages.templatetags import Library
from cms.apps.utils.templatetags.permalinks import expand_permalinks
from cms.apps.utils.templatetags.thumbnails import generate_thumbnails


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
    try:
        page = Page.objects.get_page(page)
    except Page.DoesNotExist:
        return "#"
    return page.content.reverse(view_func)


@register.inclusion_tag("link.html", takes_context=True)
def link(context, url, title=None):
    """
    Generates a hyperlink to the given url.
    
    The link will be marked as 'here' according to the 'here' template tag.
    """
    request = context["request"]
    context = {"request": request,
               "title": title or url,
               "url": url}
    return context


# Dynamic class generation.


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


# Flow control.


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

    