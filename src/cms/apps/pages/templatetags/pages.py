"""Template tags used to render pages."""


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


# Page widgets.


@register.tag
def meta_description(parser, token):
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
    def handler(context, description=None):
        page = context["page"]
        description = description or context.get("meta_description", "")
        while not description and page:
            description = page.meta_description
            page = page.parent
        return description
    return PatternNode(parser, token, handler, ("{description}", "",))


@register.tag
def meta_keywords(parser, token):
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
    def handler(context, keywords=None):
        page = context["page"]
        keywords = keywords or context.get("meta_keywords", "")
        while not keywords and page:
            keywords = page.meta_keywords
            page = page.parent
        return keywords
    return PatternNode(parser, token, handler, ("{keywords}", "",))


@register.tag
def meta_robots(parser, token):
    """
    Renders the content of the meta robots tag for the current page::
    
        {% meta_keywords %}
    
    You can override the meta robots by setting boolean context variables called
    'robots_index', 'robots_archive' and 'robots_follow'::
    
        {% with 1 as robots_follow %}
            {% meta_robots %}
        {% endwith %}
    
    You can also provide the meta robots as three boolean arguments to this
    tag in the order 'index', 'archive' and 'follow'::
    
        {% meta_robots 1 1 1 %}
        
    """
    def handler(context, index=None, archive=None, follow=None):
        page = context["page"]
        index = index or context.get("robots_index", None)
        archive = archive or context.get("robots_archive", None)
        follow = index or context.get("robots_follow", None)
        # Follow the page ancestry, looking for robots flags.
        while page:
            if index is None and page.robots_index != None:
                index = page.robots_index
            if archive is None and page.robots_archive != None:
                archive = page.robots_archive
            if follow is None and page.robots_follow != None:
                follow = page.robots_follow
            page = page.parent
        # If no page specified robots, then default to True.
        if index is None:
            index = True
        if archive is None:
            archive = True
        if follow is None:
            follow = True
        # Generate the meta content.
        return ", ".join((index and "INDEX" or "NOINDEX", follow and "FOLLOW" or "NOFOLLOW", archive and "ARCHIVE" or "NOARCHIVE"))
    return PatternNode(parser, token, handler, ("{index} {archive} {follow}", "",))


@register.tag
def title(parser, token):
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
    def handler(context, title=None):
        page = context["page"]
        homepage = page.homepage
        # Render the title template.
        context.push()
        try:
            context.update({"title": title or context.get("title", "") or page.browser_title or page.title,
                            "site_title": homepage.browser_title or homepage.title})
            return template.loader.render_to_string("title.html", context)
        finally:
            context.pop()
    return PatternNode(parser, token, handler, ("{title}", "",))


def nav_context(page, request):
    """
    Generates a dictionary of variables related to the page, for use in page
    navigation.
    """
    page_url = page.get_absolute_url()
    return {"title": page.short_title or page.title,
            "url": page_url,
            "here": request.path.startswith(page_url),
            "page": page}
    
    
def nav_context_exact(page, request):
    """
    Generates a dictionary of variables related to the page, for use in page
    navigation.
    
    This differs to nav_context in that the page URL is matched exactly to the
    request path for determining whether the page should be considered 'here'.
    """
    page_url = page.get_absolute_url()
    return {"title": page.short_title or page.title,
            "url": page_url,
            "here": request.path == page_url,
            "page": page}

    
@register.tag
def nav_primary(parser, token):
    """
    Renders the primary navigation of the current page::
    
        {% nav_primary %}
        
    """
    def handler(context):
        page = context["page"]
        request = context["request"]
        homepage = page.homepage
        navigation = []
        if homepage.in_navigation:
            navigation.append(nav_context_exact(homepage, request))
        for entry in homepage.navigation:
            navigation.append(nav_context(entry, request))
        context.push()
        try:
            context.update({"navigation": navigation})
            return template.loader.render_to_string("nav_primary.html", context)
        finally:
            context.pop()
    return PatternNode(parser, token, handler, ("",))
    
    
@register.tag
def nav_secondary(parser, token):
    """
    Renders the secondary navigation of the current page::
    
        {% nav_secondary %}
        
    """
    def handler(context):
        page = context["page"]
        request = context["request"]
        navigation = []
        try:
            section = page.breadcrumbs[1]
        except IndexError:
            pass
        else:
            if section.in_navigation:
                navigation.append(nav_context_exact(section, request))
            for entry in section.navigation:
                navigation.append(nav_context(entry, request))
        context.push()
        try:
            context.update({"navigation": navigation})
            return template.loader.render_to_string("nav_secondary.html", context)
        finally:
            context.pop()
    return PatternNode(parser, token, handler, ("",))
    

@register.tag
def nav_tertiary(parser, token):
    """
    Renders the tertiary navigation of the current page::
    
        {% nav_tertiary %}
        
    """
    def handler(context):
        page = context["page"]
        request = context["request"]
        navigation = []
        try:
            subsection = page.breadcrumbs[2]
        except IndexError:
            pass
        else:
            if subsection.in_navigation:
                navigation.append(nav_context_exact(subsection, request))
            for entry in subsection.navigation:
                navigation.append(nav_context(entry, request))
        context.push()
        try:
            context.update({"navigation": navigation})
            return template.loader.render_to_string("nav_tertiary.html", context)
        finally:
            context.pop()
    return PatternNode(parser, token, handler, ("",))


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
        page = context["page"]
        breadcrumbs = [{"title": breadcrumb.title,
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
    return PatternNode(parser, token, handler, ("[extended]", ""))


@register.tag
def header(parser, token):
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
    def handler(context, header=None):
        page = context["page"]
        header = header or context.get("header", "") or page.title
        context.push()
        try:
            context.update({"header": header})
            return template.loader.render_to_string("header.html", context)
        finally:
            context.pop()
    return PatternNode(parser, token, handler, ("{header}", "",))

    