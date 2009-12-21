"""Pluggable page content, serialized to XML."""


import cStringIO, datetime, imp
from xml.dom import minidom
from xml.sax.saxutils import XMLGenerator

from django import template
from django.conf import settings
from django.conf.urls.defaults import url, patterns
from django.core.paginator import Paginator, EmptyPage
from django.core.serializers.xml_serializer import getInnerText
from django.core.urlresolvers import RegexURLResolver, Resolver404, Http404
from django.db.models.options import get_verbose_name
from django.http import HttpResponse
from django.shortcuts import render_to_response, redirect

from cms.apps.pages.forms import PageForm
from cms.apps.utils.optimizations import cached_getter
from cms.apps.utils import loader
from cms.apps.pages.content.helpers import Breadcrumb, NavEntry
from cms.apps.pages.content.fields import Field, CharField, TextField, HtmlField, ChoiceField, URLField, EmailField, IntegerField, PositiveIntegerField, FileField, ImageField, ModelField, BooleanField


view_id_counter = 0
    
    
def view(url):
    """
    Decorator used to mark up Content methods as view functions.
    
    Priority is an integer used to provide coarse ordering of the view
    functions.  By default, views are checked in the order that they are
    declared.  By setting the priority to positive, you can make a view be
    checked earlier in the URL resolution process.  By setting the priority to
    negative, you can ensure that a view is evaluated last.
    
    By convention, the priority of -100 is reserved for the dispatch_to_child
    view of content objects.  This ensures that all declared views are evaluated
    before it.
    """
    def decorator(func):
        global view_id_counter
        func.url = url
        view_id_counter += 1
        func.view_id = view_id_counter
        return func
    return decorator
    
    
registered_content = {}


class ContentRegistrationError(Exception):
    
    """Exception raised when content registration goes astray.""" 


def lookup(slug):
    """Looks up the given content type by type slug."""
    try:
        return registered_content[slug]
    except KeyError:
        raise ContentRegistrationError, "No content type is registered under '%s'." % slug
    
    
def get_default_content():
    """Looks up the default content class from the settings."""
    return loader.load_object(settings.DEFAULT_CONTENT)
    
    
class ContentMetaClass(type):
    
    """Metaclass for Content objects."""
    
    def __init__(self, name, bases, attrs):
        """Initializes the ContentMetaClass."""
        super(ContentMetaClass, self).__init__(name, bases, attrs)
        self.fields = []
        views = []
        for attr_name in dir(self):
            value = getattr(self, attr_name)
            # Perform metaclass programming.
            if hasattr(value, "contribute_to_class"):
                value.contribute_to_class(self, attr_name)
            # Register fields.
            if isinstance(value, Field):
                self.fields.append(value)
            # Register view functions.
            if callable(value) and hasattr(value, "view_id"):
                views.append((value.view_id, url(value.url, value, name=value.__name__)))
        # Sort fields by creation order.
        self.fields.sort(lambda a, b: cmp(a.creation_order, b.creation_order))
        # Generate the urlconf.
        views.sort(lambda a, b: cmp(a[0], b[0]))
        view_funcs = [""] + [view_func for view_id, view_func in views]
        self.urlpatterns = patterns(*view_funcs)
        # Generate a verbose name, if required.
        if not "verbose_name" in attrs:
            verbose_name = get_verbose_name(name)
            self.verbose_name = verbose_name
        if not "verbose_name_plural" in attrs:
            self.verbose_name_plural = self.verbose_name + "s"
        # Auto-register the content.
        if not "registration_key" in attrs:
            self.registration_key = name.lower()
        if not "abstract" in attrs:
            self.abstract = False
        if not self.abstract:
            registered_content[self.registration_key] = self
        
        
class ContentBase(object):
    
    """
    The base page content type.
    
    Subclasses should extend this with additional functionality.
    """
    
    __metaclass__ = ContentMetaClass
    
    # Setting abstract to True prevents registration of this content class.
    abstract = True
    
    # This must be a 64 x 64 pixel image.
    icon = settings.CMS_MEDIA_URL + "img/content-types/content.png"
    
    # The heading that the admin places this content under.
    classifier = "content"
    
    # The key that this content should be registered under.  Leave blank to use
    # the lowercase class name.
    registration_key = None
    
    # Use to override the auto-generated verbose names.
    verbose_name = None
    verbose_name_plural = None
    
    def __init__(self, page):
        """
        Initializes the page content.
        
        If page is None, then an unbound content object is created.  Not all
        methods will work in an unbound content object, but it is fine for
        generating form fields used by the admin interface.
        """
        self.page = page
        if page and page.content_data:
            self.serialized_data = page.content_data
        else:
            self.data = {}
        
    # Content serialization methods.
        
    def get_serialized_data(self):
        """Returns the content data, serialized to XML."""
        # Start the XML document.
        out = cStringIO.StringIO()
        generator = XMLGenerator(out, "utf-8")
        generator.startDocument()
        generator.startElement("content", {})
        # Generate the XML.
        for field in self.fields:
            key = field.name
            value = self.data[key]
            generator.startElement("attribute", {"name": key})
            if value is None:
                serialized_value = ""
            else:
                serialized_value = field.serialize(value)
            generator.characters(serialized_value)
            generator.endElement("attribute")
        # Return the generated XML.
        generator.endElement("content")
        generator.endDocument()
        return out.getvalue()
    
    def set_serialized_data(self, serialized_data):
        """Deserializes the given data into a dictionary."""
        # Generate a dictionary of serialized data.
        raw_data = {}
        xml_data = minidom.parseString(serialized_data.encode("utf8")).documentElement
        for element in xml_data.getElementsByTagName("attribute"):
            key = element.attributes["name"].nodeValue
            value = getInnerText(element)
            raw_data[key] = value
        # Deserialize the data using fields.
        data = {}
        for field in self.fields:
            key = field.name
            serialized_value = raw_data.get(key, "")
            value = field.deserialize(serialized_value)
            data[key] = value
        self.data = data
        
    serialized_data = property(get_serialized_data,
                               set_serialized_data,
                               doc="The serialized content data, as XML.")
        
    # Template context generators.
    
    def get_navigation(self):
        """
        Returns the sub-navigation of the page.
        
        This can be extended to add additional, programmatic entries to the
        navigation.  Navigation entries must conform to the interface of
        NavEntry.  Instances of PageBase already conform to this specification,
        alowing either to be used by this method.
        """
        return [child for child in self.page.children if child.in_navigation]
    
    navigation = property(lambda self: self.get_navigation(),
                          doc="The sub-navigation of the page.")
        
    def get_breadcrumbs(self):
        """Returns the breadcrumbs leading to this page."""
        page = self.page
        breadcrumbs = page.all_parents
        breadcrumbs.reverse()
        breadcrumbs.append(page)
        return breadcrumbs
    
    breadcrumbs = property(get_breadcrumbs,
                           doc="The breadcrumbs leading to this page.")
        
    def get_page(self, request, models, items_per_page=None, pagination_key=None):
        """Returns an object paginator for the given models."""
        items_per_page = items_per_page or settings.ITEMS_PER_PAGE
        pagination_key = pagination_key or settings.PAGINATION_KEY
        page = request.GET.get(pagination_key, 1)
        try:
            page = int(page)
        except ValueError:
            raise Http404, "'%s' is not a valid page number." % page 
        paginator = Paginator(models, items_per_page)
        try:
            page = paginator.page(page)
        except EmptyPage:
            raise Http404, "There are no models on this page."
        return page
        
    # Content view methods.
    
    @cached_getter
    def get_url_resolver(self):
        """Returns the URL resolver for this content."""
        resolver = RegexURLResolver(r"^", "cms.apps.pages.content.%s.urlpatterns" % self.__class__.__name__)
        resolver._urlconf_module = self
        return resolver
    
    url_resolver = property(get_url_resolver,
                            doc="The URL resolver for this content.")
    
    def reverse(self, view_func, *args, **kwargs):
        """Performs a reverse URL lookup."""
        return self.page.url + self.url_resolver.reverse(view_func, *args, **kwargs)
    
    def dispatch(self, request, path_info):
        """Generates a HttpResponse for this context."""
        page = self.page
        # Dispatch to the appropriate view.
        resolver = self.url_resolver
        try:
            callback, callback_args, callback_kwargs = resolver.resolve(path_info)
        except Resolver404:
            # First of all see if adding a slash will help matters.
            if settings.APPEND_SLASH:
                new_path_info = path_info + "/"
                try:
                    resolver.resolve(new_path_info)
                except Resolver404:
                    pass
                else:
                    return redirect(page.get_absolute_url() + new_path_info)
            raise Http404, "No match for the current path '%s' found in the url conf of %s." % (path_info, self.__class__.__name__)
        response = callback(self, request, *callback_args, **callback_kwargs)
        # Validate the response.
        if not isinstance(response, HttpResponse):
            raise ValueError, "The view %s.%s didn't return an HttpResponse object." % (self.__class__.__name__, callback.__name__)
        return response
    
    def render_to_response(self, request, template_name, context, **kwargs):
        """Renders this content to the response."""
        return self.render_page(request, template_name, context, self.page, **kwargs)
    
    def render_page(self, request, template_name, context, page, **kwargs):
        """Renders the given page to a HttpResponse."""
        # Generate the breadcrumbs.
        breadcrumbs = self.breadcrumbs
        # Generate SEO information
        meta_description = ""
        meta_keywords = ""
        robots_index = True
        robots_archive = True
        robots_follow = True
        for breadcrumb in breadcrumbs + [page]:
            meta_description = breadcrumb.meta_description or meta_description
            meta_keywords = breadcrumb.meta_keywords or meta_keywords
            if breadcrumb.robots_index != None:
                robots_index = bool(breadcrumb.robots_index)
            if breadcrumb.robots_archive != None:
                robots_archive = bool(breadcrumb.robots_archive)
            if breadcrumb.robots_follow != None:
                robots_follow = bool(breadcrumb.robots_follow)
        # Parse the main section.
        homepage = breadcrumbs[0]
        if len(breadcrumbs) > 1:
            section = breadcrumbs[1]
            nav_secondary = section.content.navigation
        else:
            section = None
            nav_secondary = None
        # Parse the subsection.
        if len(breadcrumbs) > 2:
            subsection = breadcrumbs[2]
            nav_tertiary = subsection.content.navigation
        else:
            subsection = None
            nav_tertiary = None
        # Snip off last breadcrumb if the page is at the current URL.
        if self.page.url == request.path:
            breadcrumbs = breadcrumbs[:-1]
        # Generate the context.
        context.setdefault("page", page)
        context.setdefault("content", self)
        context.setdefault("short_title", context.get("title") or page.short_title or page.title)
        context.setdefault("browser_title", context.get("title") or page.browser_title or page.title)
        context.setdefault("title", page.title)
        context.setdefault("meta_description", meta_description)
        context.setdefault("meta_keywords", meta_keywords)
        context.setdefault("robots_index", robots_index)
        context.setdefault("robots_archive", robots_archive)
        context.setdefault("robots_follow", robots_follow)
        context.setdefault("homepage", homepage)
        context.setdefault("breadcrumbs", breadcrumbs)
        context.setdefault("is_homepage", (page == homepage))
        context.setdefault("site_title", homepage.browser_title or homepage.title)
        context.setdefault("nav_primary", homepage.content.navigation)
        context.setdefault("section", section)
        context.setdefault("nav_secondary", nav_secondary)
        context.setdefault("subsection", subsection)
        context.setdefault("nav_tertiary", nav_tertiary)
        return render_to_response(template_name, context, template.RequestContext(request), **kwargs)
    
    @view("^$")
    def index(self, request):
        """Renders the content as a HTML page."""
        content_name = self.__class__.__name__.lower()
        template_name = ("pages/%s.html" % content_name,
                         "base.html")
        return self.render_to_response(request, template_name, {})
        
    # Administration methods.
        
    def get_form(self):
        """Returns a form used to edit this Content."""
        form_attrs = dict([(field.name, field.get_formfield(self))
                           for field in self.fields])
        Form = type("%sForm" % self.__class__.__name__, (PageForm,), form_attrs)
        return Form
    
    def get_field_names(self):
        """Returns a list of all the named fields in this Content."""
        fields = [field.name for field in self.fields]
        return fields
    
    def get_fieldsets(self):
        """Returns the fieldsets used to lay out the content form."""
        field_names = self.get_field_names()
        return (("Page content", {"fields": field_names}),)
  

DEFAULT_CONTENT_SLUG = "content"


# Permissions control.

def get_add_permission(slug):
    """Generates the add permission codename for the given slug."""
    if slug == DEFAULT_CONTENT_SLUG:
        raise ValueError, "Base content model does not have an add permission."
    return u"add_%s_page" % slug


# Content registration methods.


def autoregister():
    """
    Scans all installed applications for content.py files, and trys to import
    them.
    """
    for app in settings.INSTALLED_APPS:
        try:
            app_path = __import__(app, {}, {}, [app.split(".")[-1]]).__path__
        except AttributeError:
            continue
        try:
            imp.find_module("content", app_path)
        except ImportError:
            continue
        __import__("%s.content" % app)


# Simple base content models.


class Content(ContentBase):
    
    """The default page content associated by default with all pages."""
    
    verbose_name_plural = "content"
    
    content_primary = HtmlField("primary content",
                                required=False)
    
    def get_fieldsets(self):
        """Returns the admin fieldsets."""
        return (("Page content", {"fields": ("content_primary",)}),)

    