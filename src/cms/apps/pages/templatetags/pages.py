"""Template tags used to render pages."""


from django import template
from django.utils.html import escape

from optimizations.templatetags import simple_tag, template_tag, assignment_tag

from cms import debug
from cms.apps.pages.models import Page


register = template.Library()


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
    
    
class NavigationRenderer(object):
    
    """Renders navigation."""
    
    def __init__(self, entries, context):
        """Initializes the navigation renderer."""
        self.entries = entries
        self.context = context
    
    def __iter__(self):
        """Iterates over the entries."""
        return iter(self.entries)
        
    def __unicode__(self):
        """Renders the navigation."""
        self.context.push()
        try:
            self.context.update({
                "navigation": self.entries,
            })
            return template.loader.render_to_string("pages/navigation.html", self.context)
        finally:
            self.context.pop()
    

@simple_tag(register, takes_context=True)
@assignment_tag(register, takes_context=True, name="get_navigation")
def navigation(context, pages, section=None):
    """
    Renders a navigation list for the given pages.
    
    The pages should all be a subclass of PageBase, and possess a get_absolute_url() method.
    
    You can also specify an alias for the navigation, at which point it will be set in the
    context rather than rendered.
    """
    request = context["request"]
    # Compile the entries.
    entries = [NavigationItem(request, page) for page in pages]
    # Add the section.
    if section:
        entries = [SectionNavigationItem(request, section)] + entries
    # Render the template.
    return NavigationRenderer(entries, context)


# Page linking.


@simple_tag(register)
def page_url(page, view_func=None, *args, **kwargs):
    """Renders the URL of the given view func in the given page."""
    url = None
    if isinstance(page, basestring):
        try:
            page = Page.objects.get(permalink=page)
        except Page.DoesNotExist:
            url = "#"
    elif isinstance(page, int):
        try:
            page = Page.objects.get(pk=page)
        except Page.DoesNotExist:
            url = "#"
    if page is None:
        url = "#"
    else:
        # Get the page URL.
        if view_func is None:
            url = page.get_absolute_url()
        else:
            url = page.reverse(page, view_func, args, kwargs)
    # Return the value, or set as a context variable as appropriate.
    return escape(url)


# Page widgets.

@simple_tag(register, takes_context=True)
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
        if page:
            description = page.meta_description
    return escape(description or "")


@simple_tag(register, takes_context=True)
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
        if page:
            keywords = page.meta_keywords
    return escape(keywords or "")


@simple_tag(register, takes_context=True)
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
    # Override with context variables.
    if index is None:
        index = context.get("robots_index")
    if follow is None:
        follow = context.get("robots_follow")
    if archive is None:
        archive = context.get("robots_archive")
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


@template_tag(register, "pages/title.html", takes_context=True)
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
    return {
        "title": browser_title or context.get("title") or (page and page.browser_title) or (page and page.title) or "",
        "site_title": (homepage and homepage.browser_title) or (homepage and homepage.title) or ""
    }


@template_tag(register, "pages/breadcrumbs.html", takes_context=True)
def breadcrumbs(context, page=None, extended=False):
    """
    Renders the breadcrumbs trail for the current page::
    
        {% breadcrumbs %}
        
    To override and extend the breadcrumb trail within page applications, add
    the 'extended' flag to the tag and add your own breadcrumbs underneath::
    
        {% breadcrumbs extended=1 %}
        
    """
    request = context["request"]
    # Render the tag.
    page = page or request.pages.current
    if page:
        breadcrumb_list = [{
            "short_title": breadcrumb.short_title or breadcrumb.title,
            "title": breadcrumb.title,
            "url": breadcrumb.get_absolute_url(),
            "last": False,
            "page": breadcrumb,
        } for breadcrumb in request.pages.breadcrumbs]
    else:
        breadcrumb_list = []
    if not extended:
        breadcrumb_list[-1]["last"] = True
    # Render the breadcrumbs.
    return {
        "breadcrumbs": breadcrumb_list,
    }


@template_tag(register, "pages/header.html", takes_context=True)
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
    return {
        "header": page_header,
    }
