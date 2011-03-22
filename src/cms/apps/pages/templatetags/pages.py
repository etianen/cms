"""Template tags used to render pages."""


from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape, conditional_escape

from cms.core.html import process as process_html
from cms.core.optimizations import cached_getter
from cms.core.templatetags import PatternNode
from cms.apps.pages.models import Page


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
    

@register.tag
def content(parser, token):
    """
    Renders the named content area of the current page.
    
    For example, to render the content area called 'content_primary'::
    
        {% content "content_primary" %}
        
    If you use the 'inherited' keyword, and the page content area is blank, then
    the parent page content area will be rendered instead::
    
        {% content "content_primary" inherited %}
        
    """
    def handler(context, content_area, inherited=False):
        # Render the tag.
        page = context["page"]
        content = ""
        while not content and page:
            content_obj = page.content
            content = getattr(content_obj, content_area, "")
            if not inherited:
                break
            page = page.parent
        return html(content)
    return PatternNode(parser, token, handler, (
        "{content_area} [inherited]",
        "{content_area}",
    ))


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
            if self.view_func is None:
                url = page.get_absolute_url()
            else:
                args = [arg.resolve(context) for arg in self.args]
                kwargs = dict((key, value.resolve(context)) for key, value in self.kwargs.items())
                url = page.reverse(self.view_func, *args, **kwargs)
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
    description = description or context.get("meta_description", "")
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
    keywords = keywords or context.get("meta_keywords", "")
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
    if index is None:
        index = context.get("robots_index")
        if index is None:
            index = True
    if follow is None:
        follow = context.get("robots_follow")
        if follow is None:
            follow = True
    if archive is None:
        archive = context.get("robots_archive")
        if archive is None:
            archive = True
    # Generate the meta content.
    robots = ", ".join((index and "INDEX" or "NOINDEX", follow and "FOLLOW" or "NOFOLLOW", archive and "ARCHIVE" or "NOARCHIVE"))
    return escape(robots)


@register.simple_tag(takes_context=True)
def title(context, title=None):
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
    page = context["page"]
    homepage = Page.objects.get_homepage()
    # Render the title template.
    context.push()
    try:
        context.update({"title": title or context.get("title") or page.browser_title or page.title,
                        "site_title": homepage.browser_title or homepage.title})
        return template.loader.render_to_string("title.html", context)
    finally:
        context.pop()


class NavEntry(object):
    
    """Helper object used to display site navigation."""
    
    def __init__(self, page, current_page, nav_override=None):
        """Initializes the NavigationHelper."""
        self.page = page
        self.here = page in current_page.breadcrumbs
        self.url = page.get_absolute_url()
        self.title = page.title
        self.short_title = page.short_title or page.title
        self.current_page = current_page
        self.nav_override = nav_override

    @property
    @cached_getter
    def navigation(self):
        if self.nav_override is not None:
            return self.nav_override
        return [NavEntry(entry, self.current_page) for entry in self.page.navigation]
    
    
@register.simple_tag(takes_context=True)
def nav_primary(context):
    """
    Renders the primary navigation of the current page::
    
        {% nav_primary %}
        
    """
    page = context["page"]
    homepage = Page.objects.get_homepage()
    navigation = []
    if homepage.in_navigation:
        nav_entry = NavEntry(homepage, page, [])
        nav_entry.short_title = "Home"
        nav_entry.here = homepage == page
        navigation.append(nav_entry)
    for entry in homepage.navigation:
        navigation.append(NavEntry(entry, page))
    context.push()
    try:
        context.update({"homepage": homepage,
                        "navigation": navigation})
        return template.loader.render_to_string("nav_primary.html", context)
    finally:
        context.pop()
    
    
@register.simple_tag(takes_context=True)
def nav_secondary(context):
    """
    Renders the secondary navigation of the current page::
    
        {% nav_secondary %}
        
    """
    page = context["page"]
    try:
        section = page.breadcrumbs[1]
    except IndexError:
        section = None
        navigation = []
    else:
        navigation = [NavEntry(entry, page) for entry in section.navigation]
    context.push()
    try:
        context.update({"section": section,
                        "navigation": navigation})
        return template.loader.render_to_string("nav_secondary.html", context)
    finally:
        context.pop()
    

@register.simple_tag(takes_context=True)
def nav_tertiary(context):
    """
    Renders the tertiary navigation of the current page::
    
        {% nav_tertiary %}
        
    """
    page = context["page"]
    try:
        subsection = page.breadcrumbs[2]
    except IndexError:
        subsection = None
        navigation = []
    else:
        navigation = [NavEntry(entry, page) for entry in subsection.navigation]
    context.push()
    try:
        context.update({"subsection": subsection,
                        "navigation": navigation})
        return template.loader.render_to_string("nav_tertiary.html", context)
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
    def handler(context, extended=False):
        # Render the tag.
        page = context["page"]
        breadcrumbs = [{"short_title": breadcrumb.short_title or breadcrumb.title,
                        "title": breadcrumb.title,
                        "url": breadcrumb.get_absolute_url(),
                        "last": False,
                        "page": breadcrumb}
                       for breadcrumb in page.breadcrumbs]
        if not extended:
            if len(breadcrumbs) == 1:
                # Display no breadcrumbs on the homepage.
                breadcrumbs = []
            else:
                breadcrumbs[-1]["last"] = True
        # Render the breadcrumbs.
        context.push()
        try:
            context.update({"breadcrumbs": breadcrumbs,})
            return template.loader.render_to_string("breadcrumbs.html", context)
        finally:
            context.pop()
    return PatternNode(parser, token, handler, (
        "[extended]",
        ""
    ))


@register.simple_tag(takes_context=True)
def header(context, header=None):
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
    page = context["page"]
    header = header or context.get("header") or context.get("title") or page.title
    context.push()
    try:
        context.update({
            "header": header
        })
        return template.loader.render_to_string("header.html", context)
    finally:
        context.pop()