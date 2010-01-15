"""Template tags used by the CMS."""


from django import template
from django.utils.safestring import mark_safe

from cms.apps.pages.models import Page
from cms.apps.pages.templatetags import PatternNode
from cms.apps.pages.templatetags.permalinks import expand_permalinks
from cms.apps.pages.templatetags.thumbnails import generate_thumbnails


register = template.Library()


# HTML processing.


@register.filter
def html(text):
    """
    Processes HTML text.
    
    The text is checked for permalinks embedded in <a> tags, expanding the
    permalinks to their referenced URL. Images containing a permalink source
    are checked for size and thumbnailed as appropriate.
    """
    if not text:
        return ""
    text = expand_permalinks(text)
    text = generate_thumbnails(text)
    return mark_safe(text)
    

@register.tag
def content(parser, token):
    """
    Renders the named content area of the current page.
    
    For example, to render the content area called 'content_primary'::
    
        {% content "content_primary" %}
        
    If you use the 'inherit' keyword, and the page content area is blank, then
    the parent page content area will be rendered instead::
    
        {% content "content_primary" inherited %}
    """
    def handler(context, content_area, inherited=False):
        page = context["page"]
        content = ""
        while not content:
            content_obj = page.content
            content = getattr(content_obj, content_area, "")
            if not inherited:
                break
            if page.parent:
                page = page.parent
        return html(content)
    return PatternNode(parser, token, handler, ("{content_area} [inherited]", "{content_area}"))


# Page linking.


class PageUrlNode(template.Node):
    
    """Renders the page_url tag."""
    
    def __init__(self, page, view_func, args, kwargs, varname):
        """Initializes the PageUrlNode."""
        self.page = page
        self.view_func = view_func
        self.args = args
        self.kwargs = kwargs
        self.varname = varname
        
    def render(self, context):
        """Renders the PageUrlNode."""
        page = self.page.resolve(context)
        # Get the page URL.
        try:
            page = Page.objects.get_page(page)
        except Page.DoesNotExist:
            url = "#"
        else:
            args = [arg.resolve(context) for arg in self.args]
            kwargs = dict((key, value.resolve(context)) for key, value in self.kwargs.items())
            url = page.content.reverse(self.view_func, *args, **kwargs)
        # Return the value, or set as a context variable as appropriate.
        if self.varname:
            context[self.varname] = url
            return ""
        else:
            return url


@register.tag
def page_url(parser, token):
    """Renders the URL of the given view func in the given page."""
    contents = token.split_contents()
    tag_name = contents[0]
    contents = contents[1:]
    # Attempt to parse the varname.
    try:
        if contents.index("as") == len(contents) - 2:
            varname = contents[-1]
            contents = contents[:-2]
        else:
            raise template.TemplateSyntaxError, "%s tag expects only one argument after 'as' statement" % tag_name
    except ValueError:
        # No varname was specified.
        varname = None
    # Attempt to parse the page.
    try:
        page = parser.compile_filter(contents[0])
    except IndexError:
        raise template.TemplateSyntaxError, "No page specified in %s tag" % tag_name
    # Attempt to parse the view func.
    try:
        view_func = contents[1]
    except IndexError:
        view_func = "index"
    # Parse all remaining token as arguments.
    args = []
    kwargs = {}
    for argument in "".join(contents[2:]).split(","):
        if "=" in argument:
            key, value = argument.split("=")
            kwargs[key.strip()] = parser.compile_filter(value.strip())
        else:
            args.append(parser.compile_filter(argument.strip()))
    # Create the node.
    return PageUrlNode(page, view_func, args, kwargs, varname)


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


@register.tag
def breadcrumbs(parser, token):
    """Renders the breadcrumbs trail for the page."""
    def handler(context, extended=False):
        page = context["page"]
        breadcrumbs = [{"title": breadcrumb.title,
                        "url": breadcrumb.get_absolute_url(),
                        "final": False}
                       for breadcrumb in page.breadcrumbs]
        if not extended:
            breadcrumbs[-1]["final"] = True
        context = {"breadcrumbs": breadcrumbs,}
        return template.loader.render_to_string("breadcrumbs.html", context)
    return PatternNode(parser, token, handler, ("[extended]", ""))


@register.tag
def breadcrumb_link(parser, token):
    """Renders a breadcrumb in the breadcrumb trail."""
    def handler(context, title, url):
        context = {"title": title,
                   "url": url}
        return template.loader.render_to_string("breadcrumb_link.html", context)
    return PatternNode(parser, token, handler, ("{title} {url}",))


@register.tag
def breadcrumb_title(parser, token):
    """Renders the final title entry in the breadcrumb trail."""
    def handler(context, title):
        context = {"title": title}
        return template.loader.render_to_string("breadcrumb_title.html", context)
    return PatternNode(parser, token, handler, ("{title}",))


@register.inclusion_tag("header.html", takes_context=True)
def header(context):
    """"Renders the page header."""
    page = context["page"]
    context = {"page": page}
    return context
    
    