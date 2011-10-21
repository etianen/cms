"""Template tags used to render pages."""


from django import template
from django.template import Node, TemplateSyntaxError
from django.utils.safestring import mark_safe
from django.utils.html import escape, conditional_escape

from cms.core.html import process as process_html
from cms.core.templatetags import PatternNode
from cms.core.models import PageBase
from cms.core import debug


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
    text = process_html(text)
    return mark_safe(text)


# Navigation.

class NavigationItem(object):
    
    """An item in a navigation list."""
    
    def __init__(self, request, page):
        """Initializes the NavigationItem."""
        self._request = request
        self.url = page.get_absolute_url()
        self.page = page
        self.title = page.title
        self.short_title = unicode(page)
        self.here = request.path.startswith(self.url)
        
    @property
    @debug.print_exc
    def navigation(self):
        """Returns the sub-navigation."""
        return self.page.navigation
        
    def __unicode__(self):
        """Returns a unicode representation."""
        return self.short_title


class SectionNavigationItem(NavigationItem):
    
    """An item in a navigation list with no navigation."""
    
    def __init__(self, request, page):
        """Initialzies the SectionNavigationItem."""
        super(SectionNavigationItem, self).__init__(request, page)
        self.here = request.path == self.url
    
    navigation = ()
    

@register.tag
def navigation(parser, token):
    """
    Renders a navigation list for the given pages.
    
    The pages should all be a subclass of PageBase, and possess a get_absolute_url() method.
    
    You can also specify an alias for the navigation, at which point it will be set in the
    context rather than rendered.
    """
    def handler(context, pages, section=None, alias=None):
        request = context["request"]
        # Compile the entries.
        entries = [NavigationItem(request, page) for page in pages]
        # Add the section.
        if section:
            entries = [SectionNavigationItem(request, section)] + entries
        # Set to alias, maybe.
        if alias:
            context[alias] = entries
            return ""
        # Render the template.
        context.push()
        try:
            context.update({
                "navigation": entries
            })
            return template.loader.render_to_string("navigation.html", context)
        finally:
            context.pop()
    return PatternNode(parser, token, handler, (
        "{pages} with {section} as [alias]",
        "{pages} as [alias]",
        "{pages} with {section}",
        "{pages}",
    ))


# Page linking.

class PageUrlNode(Node):
    
    """Renders the page_url tag."""
    
    def __init__(self, page, view_func, args, kwargs, varname):
        """Initializes the PageUrlNode."""
        super(PageUrlNode, self).__init__()
        self.page = page
        self.view_func = view_func
        self.args = args
        self.kwargs = kwargs
        self.varname = varname
        
    def render(self, context):
        """Renders the PageUrlNode."""
        request = context["request"]
        page = self.page.resolve(context)
        # Look up pages, if given an id.
        url = None
        if not isinstance(page, PageBase):
            page = request.pages.get(page)
        if page is None:
            url = "#"
        else:
            # Get the page URL.
            if self.view_func is None:
                url = page.get_absolute_url()
            else:
                args = [arg.resolve(context) for arg in self.args]
                kwargs = dict((key, value.resolve(context)) for key, value in self.kwargs.items())
                url = request.pages.reverse(page, self.view_func, *args, **kwargs)
        # Return the value, or set as a context variable as appropriate.
        if self.varname:
            context[self.varname] = url
            return ""
        else:
            return escape(url)


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
            raise TemplateSyntaxError("{tag_name} tag expects only one argument after 'as' statement".format(
                tag_name = tag_name,
            ))
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
        view_func = None
    # Parse all remaining token as arguments.
    args = []
    kwargs = {}
    argstring = "".join(contents[2:])
    if argstring:
        for argument in argstring.split(","):
            if "=" in argument:
                key, value = argument.split("=")
                kwargs[key.strip()] = parser.compile_filter(value.strip())
            else:
                args.append(parser.compile_filter(argument.strip()))
    # Create the node.
    return PageUrlNode(page, view_func, args, kwargs, varname)


# Page widgets.

@register.simple_tag(takes_context=True)
def meta_description(context, description=None):
    """
    Renders the content of the meta description tag for the current page::
    
        {% meta_description %}
    
    You can override the meta description by setting a context variable called
    'meta_description'::
    
        {% with "foo" as meta_description %}
            {% meta_description %}
        {% endwith %}
    
    You can also provide the meta description as an argument to this tag::
    
        {% meta_description "foo" %}
        
    """
    if description is None:
        description = context.get("meta_description")
    if description is None:
        request = context["request"]
        page = request.pages.current
        description = page.meta_description
    return conditional_escape(description)


@register.simple_tag(takes_context=True)
def meta_keywords(context, keywords=None):
    """
    Renders the content of the meta keywords tag for the current page::
    
        {% meta_keywords %}
    
    You can override the meta keywords by setting a context variable called
    'meta_keywords'::
    
        {% with "foo" as meta_keywords %}
            {% meta_keywords %}
        {% endwith %}
    
    You can also provide the meta keywords as an argument to this tag::
    
        {% meta_keywords "foo" %}
        
    """
    if keywords is None:
        keywords = context.get("meta_keywords")
    if keywords is None:
        request = context["request"]
        page = request.pages.current
        keywords = page.meta_keywords
    return conditional_escape(keywords)


@register.simple_tag(takes_context=True)
def meta_robots(context, index=None, follow=None, archive=None):
    """
    Renders the content of the meta robots tag for the current page::
    
        {% meta_robots %}
    
    You can override the meta robots by setting boolean context variables called
    'robots_index', 'robots_archive' and 'robots_follow'::
    
        {% with 1 as robots_follow %}
            {% meta_robots %}
        {% endwith %}
    
    You can also provide the meta robots as three boolean arguments to this
    tag in the order 'index', 'follow' and 'archive'::
    
        {% meta_robots 1 1 1 %}
        
    """
    request = context["request"]
    # Override with context variables.
    if index is None:
        index = context.get("robots_index")
    if follow is None:
        follow = context.get("robots_follow")
    if archive is None:
        archive = context.get("robots_archive")
    # Override with page variables.
    current_page = request.pages.current
    if current_page:
        index, follow, archive = current_page.resolve_meta_robots(index, follow, archive)
    else:
        index, follow, archive = None, None, None
    # Final override, set to True.
    if index is None:
        index = True
    if follow is None:
        follow = True
    if archive is None:
        archive = True
    # Generate the meta content.
    robots = ", ".join((
        index and "INDEX" or "NOINDEX",
        follow and "FOLLOW" or "NOFOLLOW",
        archive and "ARCHIVE" or "NOARCHIVE",
    ))
    return escape(robots)


@register.simple_tag(takes_context=True)
def title(context, browser_title=None):
    """
    Renders the title of the current page::
        
        {% title %}
    
    You can override the title by setting a context variable called 'title'::
    
        {% with "foo" as title %}
            {% title %}
        {% endwith %}
        
    You can also provide the title as an argument to this tag::
        
        {% title "foo" %}
    
    """
    request = context["request"]
    page = request.pages.current
    homepage = request.pages.homepage
    # Render the title template.
    context.push()
    try:
        context.update({
            "title": browser_title or context.get("title") or (page and page.browser_title) or (page and page.title) or "",
            "site_title": (homepage and homepage.browser_title) or (homepage and homepage.title) or ""
        })
        return template.loader.render_to_string("title.html", context)
    finally:
        context.pop()


@register.tag
def breadcrumbs(parser, token):
    """
    Renders the breadcrumbs trail for the current page::
    
        {% breadcrumbs %}
        
    To override and extend the breadcrumb trail within page applications, add
    the 'extended' flag to the tag and add your own breadcrumbs underneath::
    
        {% breadcrumbs extended %}
        
    """
    @debug.print_exc
    def handler(context, page=None, extended=False):
        request = context["request"]
        # Render the tag.
        page = page or request.pages.current
        breadcrumb_list = [{
            "short_title": breadcrumb.short_title or breadcrumb.title,
            "title": breadcrumb.title,
            "url": breadcrumb.get_absolute_url(),
            "last": False,
            "page": breadcrumb,
        } for breadcrumb in page.breadcrumbs]
        if not extended:
            breadcrumb_list[-1]["last"] = True
        # Render the breadcrumbs.
        context.push()
        try:
            context.update({"breadcrumbs": breadcrumb_list,})
            return template.loader.render_to_string("breadcrumbs.html", context)
        finally:
            context.pop()
    return PatternNode(parser, token, handler, (
        "for {page} [extended]",
        "[extended]",
        "for {page}",
        ""
    ))


@register.simple_tag(takes_context=True)
def header(context, page_header=None):
    """
    Renders the header for the current page::
    
        {% header %}
        
    You can override the page header by providing a 'header' or 'title' context
    variable. If both are present, then 'header' overrides 'title'::
    
        {% with "foo" as header %}
            {% header %}
        {% endwith %}
        
    You can also provide the header as an argument to this tag::
    
        {% header "foo" %}
        
    """
    request = context["request"]
    page_header = page_header or context.get("header") or context.get("title") or request.pages.current.title
    context.push()
    try:
        context.update({
            "header": page_header
        })
        return template.loader.render_to_string("header.html", context)
    finally:
        context.pop()