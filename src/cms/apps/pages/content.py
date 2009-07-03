"""Pluggable page content, serialized to XML."""


import cStringIO, datetime, imp, types, re
from xml.dom import minidom
from xml.sax.saxutils import XMLGenerator

from django import forms, template
from django.conf import settings
from django.conf.urls.defaults import url, patterns
from django.contrib.admin.widgets import AdminTextInputWidget, AdminTextareaWidget
from django.core.serializers.xml_serializer import getInnerText
from django.core.urlresolvers import RegexURLResolver, Resolver404, Http404
from django.db.models.options import get_verbose_name
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseServerError
from django.shortcuts import render_to_response
from django.utils.html import strip_tags
from django.utils.text import capfirst

from cms.apps.pages.forms import PageForm, HtmlWidget
from cms.apps.pages.optimizations import cached_getter


class Field(object):
    
    """A field within a Content object."""
    
    creation_counter = 0
    
    form_field = forms.CharField
    
    def __init__(self, label=None, required=False, default=None, help_text=""):
        """"Initializes the Field."""
        self.label = label
        self.required = required
        self.default = default
        self.help_text = help_text
        Field.creation_counter += 1
        self.creation_order = self.creation_counter
    
    def contribute_to_class(self, cls, name):
        """Called automatically by the ContentMetaClass on class creation."""
        self.name = name

    def get_value_from_object(self, obj):
        """Retrieves the field value from the given content object."""
        return obj.data.get(self.name, self.default)
    
    def __get__(self, obj, cls=None):
        """Retrieves the value from the Content object."""
        if obj is None:
            return self
        return self.get_value_from_object(obj)

    def __set__(self, obj, value):
        """Sets the value in the Content object."""
        obj.data[self.name] = value
        
    def get_formfield_attrs(self, obj):
        """Returns the default attributes for a form field."""
        initial = self.get_value_from_object(obj)
        attrs = {"label": self.label and capfirst(self.label) or None,
                 "required": self.required,
                 "help_text": self.help_text,
                 "widget": AdminTextInputWidget,
                 "initial": initial}
        return attrs
        
    def get_formfield(self, obj):
        """Returns a form field for this content field."""
        kwargs = self.get_formfield_attrs(obj)
        return self.form_field(**kwargs)
    
    def serialize(self, value):
        """Serializes given value as a unicode string."""
        return unicode(value)
    
    def deserialize(self, value):
        """Converts the value from a unicode string into a Python object."""
        return value
    

class CharField(Field):
    
    """A simple character data field."""
    
    def __init__(self, label=None, max_length=100, **kwargs):
        """Initializes the CharField."""
        super(CharField, self).__init__(label, **kwargs)
        self.max_length = max_length
        
    def get_formfield_attrs(self, obj):
        """Adds the max length to the default attributes."""
        attrs = super(CharField, self).get_formfield_attrs(obj)
        attrs["max_length"] = self.max_length
        return attrs
    
    
class TextField(Field):
    
    """A text data field."""
    
    def get_formfield_attrs(self, obj):
        """Changes the widget of the form field to a text area."""
        attrs = super(TextField, self).get_formfield_attrs(obj)
        attrs["widget"] = AdminTextareaWidget
        return attrs
            
    
class HtmlField(TextField):
    
    """A HTML rich text field."""
    
    def get_formfield_attrs(self, obj):
        """Changes the widget of the form field to a text area."""
        attrs = super(HtmlField, self).get_formfield_attrs(obj)
        attrs["widget"] = HtmlWidget
        return attrs
    
    
class ChoiceField(Field):
    
    """A field that allows a number of text choices."""
    
    form_field = forms.ChoiceField
    
    def __init__(self, choices, label=None, **kwargs):
        """Initializes the ChoiceField."""
        super(ChoiceField, self).__init__(label, **kwargs)
        self.choices = choices
        
    def get_formfield_attrs(self, obj):
        """Primes the choices in the form field."""
        attrs = super(ChoiceField, self).get_formfield_attrs(obj)
        attrs["choices"] = self.choices
        del attrs["widget"]
        return attrs
    
    
class URLField(CharField):
    
    """A URL data field."""
    
    form_field = forms.URLField
    
    
class EmailField(CharField):
    
    """An Email data field."""
    
    form_field = forms.EmailField
    
    
class IntegerField(Field):
    
    """A field that holds an integer number."""
    
    form_field = forms.IntegerField
    
    def __init__(self, label=None, min_value=None, max_value=None, **kwargs):
        """Initializes the IntegerField."""
        super(IntegerField, self).__init__(label, **kwargs)
        self.min_value = min_value
        self.max_value = max_value
        
    def get_formfield_attrs(self, obj):
        """Sets the min and max value attributes of the field."""
        attrs = super(IntegerField, self).get_formfield_attrs(obj)
        attrs["min_value"] = self.min_value
        attrs["max_value"] = self.max_value
        return attrs
    
    def deserialize(self, value):
        """Converts the value from a unicode string into a Python object."""
        return int(value)
    
    
class PositiveIntegerField(IntegerField):
    
    """A field that only holds positive integer numbers."""
    
    def __init__(self, label=None, max_value=None, **kwargs):
        """Initializes the PositiveIntegerField."""
        super(PositiveIntegerField, self).__init__(label, 0, max_value, **kwargs)
    
    
# View processing.
    
    
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
            setattr(self, "verbose_name", verbose_name)
        if not "verbose_name_plural" in attrs:
            self.verbose_name_plural = self.verbose_name + "s"
        
        
class Breadcrumb(object):
    
    """
    An entry in the breadcrumb trail.
    
    This conforms to the same interface as Page, allowing both to be used
    as entries in the breadcrumb trail.
    """
    
    def __init__(self, title, url):
        """Initializes the Breadcrumb."""
        self.title = title
        self.url = url
    
    def __unicode__(self):
        """Returns the title of the NavEntry."""
        return self.title
        
        
class NavEntry(Breadcrumb):
    
    """
    An entry in the site navigation.
    
    This conforms to the same interface as Page, allowing both to be used
    as entries in the site navigation.
    """
    
    def __init__(self, title, url, navigation=None):
        """Initializes the NavEntry."""
        super(NavEntry, self).__init__(title, url)
        self.navigation = navigation or ()
        
        
class ContentBase(object):
    
    """
    The base page content type.
    
    Subclasses should extend this with additional functionality.
    """
    
    __metaclass__ = ContentMetaClass
    
    # This must be a 64 x 64 pixel image.
    icon = settings.CMS_MEDIA_URL + "img/content-types/content.png"
    
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
        xml_data = minidom.parseString(serialized_data).documentElement
        for element in xml_data.getElementsByTagName("attribute"):
            key = element.attributes["name"].nodeValue
            value = getInnerText(element)
            raw_data[key] = value
        # Deserialize the data using fields.
        data = {}
        for field in self.fields:
            key = field.name
            serialized_value = raw_data.get(key, "")
            if serialized_value == "":
                value = None
            else:
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
        return self.page.navigation
    
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
        
    # Content view method.
    
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
                    result = resolver.resolve(new_path_info)
                except Resolver404:
                    pass
                else:
                    return HttpResponseRedirect(page.get_absolute_url() + new_path_info)
            raise Http404, "No match for the current path '%s' found in the url conf of %s." % (path_info, self.__class__.__name__)
        response = callback(self, request, *callback_args, **callback_kwargs)
        # Validate the response.
        if not isinstance(response, HttpResponse):
            raise ValueError, "The view %s.%s didn't return an HttpResponse object." % (self.__class__.__name__, callback.__name__)
        return response
    
    def render_to_response(self, request, template_name, context, **kwargs):
        """Renders this content to the response."""
        return self.render_page(self.page, request, template_name, context, **kwargs)
    
    def render_page(self, page, request, template_name, context, **kwargs):
        """Renders the given page to a HttpResponse."""
        if not page.is_published:
            if not (request.user.is_authenticated() and request.user.is_staff and request.user.is_active):
                raise Http404, "The page '%s' has not been published yet." % page
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

class ContentRegistrationError(Exception):
    
    """Exception raised when content registration goes wrong."""


registered_content = {}


def register(content_cls, slug=None):
    """
    Registers the given content type with this class under the given slug.
    """
    slug = slug or content_cls.__name__.lower()
    registered_content[slug] = content_cls
  
  
def unregister(slug):
    """Unregisters the content type associated with the given slug."""
    try:
        del registered_content[slug]
    except KeyError:
        raise ContentRegistrationError, "No content type is registered under '%s'." % slug


def lookup(slug):
    """Looks up the given content type by type slug."""
    try:
        return registered_content[slug]
    except KeyError:
        raise ContentRegistrationError, "No content type is registered under '%s'." % slug


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


CONTENT_AREA_NAMES = tuple([name for name, label in settings.CONTENT_AREAS])


class Content(ContentBase):
    
    """The default page content associated by default with all pages."""
    
    verbose_name_plural = "content"
    
    for name, label in settings.CONTENT_AREAS:
        locals()[name] = HtmlField(label)      


register(Content)

    