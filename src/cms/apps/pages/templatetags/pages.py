"""Template tags used by the CMS."""


from django import template
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


CONTENT_INHERIT_KEYWORD = "inherit"


class ContentNode(template.Node):
    
    """Renderer for the 'content' template tag."""
    
    def __init__(self, content_area, inherited):
        """Initializes the ContentNode."""
        super(ContentNode, self).__init__()
        self.content_area = content_area
        self.inherited = inherited
        
    def render(self, context):
        """Renders the node."""
        try:
            content_obj = context["content"]
        except IndexError:
            raise template.VariableDoesNotExist, "The context does not contain a page content object."
        content = ""
        while not content:
            content = getattr(content_obj, self.content_area, "")
            if not self.inherited:
                break
            if content_obj.page.parent:
                content_obj = content_obj.page.parent.content
        return html(content)
    

@register.tag
def content(parser, token):
    """
    Renders the named content area of the current page.
    
    For example, to render the content area called 'content_primary'::
    
        {% content content_primary %}
        
    If you use the 'inherit' keyword, and the page content area is blank, then
    the parent page content area will be rendered instead::
    
        {% content content_primary inherit %}
    """
    contents = token.split_contents()
    content_length = len(contents)
    tag_name = contents[0]
    if content_length == 2 or (content_length == 3 and contents[2] == CONTENT_INHERIT_KEYWORD):
        content_area = contents[1]
        inherited = content_length == 3
        return ContentNode(content_area, inherited)
    else:
        raise template.TemplateSyntaxError, "'%(tag_name)s' tags should use the following format: %(tag_name)s {content_area} [inherit]" % {"tag_name": tag_name}


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

    