"""Template tags used by the CMS."""


from django import template
from django.utils.safestring import mark_safe

from cms.apps.pages.models import Page
from cms.apps.pages.templatetags.permalinks import expand_permalinks
from cms.apps.pages.templatetags.thumbnails import generate_thumbnails


register = template.Library()


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
            page = context["page"]
            content_obj = page.content
        except IndexError:
            raise template.VariableDoesNotExist, "The context does not contain a page object."
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


@register.inclusion_tag("here.html", takes_context=True)
def here(context, url):
    """
    Returns 'here' if the url is at the start of the current request path.
    """
    request = context["request"]
    is_here = request.path.startswith(url)
    context = {"is_here": is_here}
    return context


@register.inclusion_tag("here.html", takes_context=True)
def here_exact(context, url):
    """
    Returns 'here' if the url is exactly equal to current request path.
    """
    request = context["request"]
    is_here = request.path == url
    context = {"is_here": is_here}
    return context


@register.inclusion_tag("first.html", takes_context=True)
def first(context):
    """Returns 'first' on the first iteration of the parent for loop."""
    is_first = context["forloop"]["first"]
    context = {"is_first": is_first}
    return context


@register.inclusion_tag("last.html", takes_context=True)
def last(context):
    """Returns 'last' on the last iteration of the parent for loop."""
    is_last = context["forloop"]["last"]
    context = {"is_last": is_last}
    return context


# Page widgets.


@register.inclusion_tag("title.html", takes_context=True)
def title(context):
    """Renders the title of the page."""
    page = context["page"]
    homepage = Page.objects.get_homepage()
    context = {"page": page,
               "homepage": homepage}
    return context

    
@register.inclusion_tag("meta_description.html", takes_context=True)
def meta_description(context):
    """Renders the meta description."""
    page = context["page"]
    description = ""
    while not description and page:
        description = page.meta_description
        page = page.parent
    context = {"description": description}
    return context


@register.inclusion_tag("meta_keywords.html", takes_context=True)
def meta_keywords(context):
    """Renders the meta description."""
    page = context["page"]
    keywords = ""
    while not keywords and page:
        keywords = page.meta_keywords
        page = page.parent
    context = {"keywords": keywords}
    return context


@register.inclusion_tag("meta_robots.html", takes_context=True)
def meta_robots(context):
    """Renders the meta robots."""
    page = context["page"]
    index = None
    archive = None
    follow = None
    while page:
        if index is None and page.robots_index != None:
            index = page.robots_index
        if archive is None and page.robots_archive != None:
            archive = page.robots_archive
        if follow is None and page.robots_follow != None:
            follow = page.robots_follow
        page = page.parent
    if index is None:
        index = True
    if archive is None:
        archive = True
    if follow is None:
        follow = True
    context = {"index": index,
               "archive": archive,
               "follow": follow}
    return context


@register.inclusion_tag("nav_primary.html", takes_context=True)
def nav_primary(context):
    """Renders the primary navigation."""
    homepage = Page.objects.get_homepage()
    page = context["page"]
    request = context["request"]
    nav_primary = homepage.navigation
    context = {"homepage": homepage,
               "page": page,
               "nav_primary": nav_primary,
               "request": request}
    return context
    
    
@register.inclusion_tag("nav_secondary.html", takes_context=True)
def nav_secondary(context):
    """Renders the secondary navigation."""
    request = context["request"]
    page = context["page"]
    breadcrumbs = page.breadcrumbs
    if len(breadcrumbs) >= 2:
        section = breadcrumbs[1]
        nav_secondary = section.navigation
    else:
        section = None
        nav_secondary = None
    context = {"section": section,
               "page": page,
               "nav_secondary": nav_secondary,
               "request": request}
    return context
    

@register.inclusion_tag("nav_tertiary.html", takes_context=True)
def nav_tertiary(context):
    """Renders the tertiary navigation."""
    request = context["request"]
    page = context["page"]
    breadcrumbs = page.breadcrumbs
    if len(breadcrumbs) >= 3:
        subsection = breadcrumbs[2]
        nav_tertiary = subsection.navigation
    else:
        section = None
        nav_tertiary = None
    context = {"subsection": section,
               "page": page,
               "nav_tertiary": nav_tertiary,
               "request": request}
    return context


@register.inclusion_tag("breadcrumbs.html", takes_context=True)
def breadcrumbs(context):
    """Renders the page breadcrumb trail."""
    page = context["page"]
    context = {"page": page}
    return context


@register.inclusion_tag("header.html", takes_context=True)
def header(context):
    """"Renders the page header."""
    page = context["page"]
    context = {"page": page}
    return context
    
    