"""Pluggable page content, serialized to XML."""


import cStringIO, datetime, types
from xml.dom import minidom
from xml.sax.saxutils import XMLGenerator

from django import forms, template
from django.conf import settings
from django.conf.urls.defaults import url, patterns
from django.contrib.admin.widgets import AdminTextInputWidget, AdminTextareaWidget
from django.core.urlresolvers import RegexURLResolver, Resolver404, Http404
from django.db.models.options import get_verbose_name
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, HttpResponseServerError
from django.shortcuts import render_to_response
from django.utils.html import strip_tags

from cms.apps.pages.forms import PageForm, HtmlWidget
from cms.apps.pages.optimizations import cached_getter
from cms.apps.pages.html import first_paragraph


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
        attrs = {"label": self.label and self.label.capitalize() or None,
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
    
    
class TextField(CharField):
    
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
    
    
class URLField(CharField):
    
    """A URL data field."""
    
    form_field = forms.URLField
    
    
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
    
    
view_id_counter = 0
    
    
def view(url, priority=0):
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
        func.view_priority = priority
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
                views.append((value.view_priority, value.view_id, url(value.url, value)))
        # Sort fields by creation order.
        self.fields.sort(lambda a, b: cmp(a.creation_order, b.creation_order))
        # Generate the urlconf.
        views.sort(lambda a, b: cmp(-a[0], -b[0]) or cmp(a[1], b[1]))
        view_funcs = [""] + [view_func for view_priority, view_id, view_func in views]
        self.urlpatterns = patterns(*view_funcs)
        # Generate a verbose name, if required.
        if not "verbose_name" in attrs:
            verbose_name = get_verbose_name(name)
            setattr(self, "verbose_name", verbose_name)
        if not "verbose_name_plural" in attrs:
            self.verbose_name_plural = self.verbose_name + "s"
        
        
class LazyNavigation(object):
    
    """
    A wrapper around a callable that is only evaluated at the last minute to
    generate page navigation.
    """
    
    def __init__(self, callable):
        """Initializes the LazyNavigation."""
        self._callable = callable
        
    @cached_getter
    def get_list(self):
        """Generates the list of navigation items."""
        return self._callable()
    
    def __len__(self):
        """Delegates to the wrapped list."""
        return self.get_list().__len__()
    
    def __getitem__(self, key):
        """Delegates to the wrapped list."""
        return self.get_list().__getitem__(key)
    
    def __setitem__(self, key, value):
        """Delegates to the wrapped list."""
        return self.get_list().__setitem__(key, value)
    
    def __delitem__(self, key):
        """Delegates to the wrapped list."""
        return self.get_list().__delitem__(key)
    
    def __iter__(self):
        """Delegates to the wrapped list."""
        return self.get_list().__iter__()
        

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
            serialized_value = field.serialize(value)
            generator.characters(serialized_value)
            generator.endElement("attribute")
        # Return the generated XML.
        generator.endElement("content")
        generator.endDocument()
        return out.getvalue()
    
    def _get_element_value(self, element):
        """Reads the content of the node as a unicode object."""
        text = []
        for child in element.childNodes:
            if child.nodeType == child.TEXT_NODE or child.nodeType == child.CDATA_SECTION_NODE:
                text.append(child.data)
            elif child.nodeType == child.ELEMENT_NODE:
                text.extend(self._get_element_value(child))
        return u"".join(text)
    
    def set_serialized_data(self, serialized_data):
        """Deserializes the given data into a dictionary."""
        # Generate a dictionary of serialized data.
        raw_data = {}
        xml_data = minidom.parseString(serialized_data).documentElement
        for element in xml_data.getElementsByTagName("attribute"):
            key = element.attributes["name"].nodeValue
            value = self._get_element_value(element)
            raw_data[key] = value
        # Deserialize the data using fields.
        data = {}
        for field in self.fields:
            key = field.name
            serialized_value = raw_data[key]
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
        
        This is returned in the form of a dictionary of 'title' and 'url'.
        An optional item is 'navigation', which should be a list of sub
        navigation.  Another optional item is 'page', which should be an
        instance of PageBase that this navigation item represents.
        """
        navigation = []
        for child in self.page.published_children:
            if child.in_navigation:
                navigation_context = {"title": child.short_title or child.title,
                                      "url": child.get_absolute_url(),
                                      "navigation": LazyNavigation(lambda: child.navigation),
                                      "page": child}
                navigation.append(navigation_context)
        return navigation
    
    navigation = property(lambda self: self.get_navigation(),
                          doc="The sub-navigation of the page.")
    
    def get_breadcrumbs(self):
        """
        Returns the breadcrumbs to this page.
        
        This is returned in the form of a dictionary of 'title' and 'url'.
        An optional item is 'page', which should be an instance of PageBase that
        this navigation item represents.
        
        This list should not include the current page.
        """
        page = self.page
        # Add parent breadcrumbs.
        if page.parent:
            parent = page.parent
            breadcrumbs = parent.content.breadcrumbs
            breadcrumb_context = {"title": parent.short_title or parent.title,
                                  "url": parent.get_absolute_url(),
                                  "page": parent}
            breadcrumbs.append(breadcrumb_context)
        else:
            breadcrumbs = []
        return breadcrumbs 
        
    breadcrumbs = property(lambda self: self.get_breadcrumbs(),
                           doc="The breadcrumbs to this page.")
        
    # Content view method.
    
    @cached_getter
    def get_url_resolver(self):
        """Returns the URL resolver for this content."""
        resolver = RegexURLResolver(r"^", "cms.apps.pages.content.%s.urlpatterns" % self.__class__.__name__)
        resolver._urlconf_module = self
        return resolver
    
    url_resolver = property(get_url_resolver,
                            doc="The URL resolver for this content.")
    
    def dispatch(self, request, path_info, default_kwargs=None):
        """Generates a HttpResponse for this context."""
        page = self.page
        # Update the request.
        request.breadcrumbs.append(self.page)
        # Dispatch to the appropriate view.
        resolver = self.url_resolver
        try:
            callback, callback_args, callback_kwargs = resolver.resolve(path_info)
        except Resolver404:
            if settings.APPEND_SLASH:
                new_path_info = path_info + "/"
                try:
                    result = resolver.resolve(new_path_info)
                except Resolver404:
                    pass
                else:
                    return HttpResponseRedirect(page.get_absolute_url() + new_path_info)
            raise Http404, "No match for the current path '%s' found in the url conf of %s." % (path_info, self.__class__.__name__)
        default_kwargs = default_kwargs or {}
        default_kwargs.update(callback_kwargs)
        response = callback(self, request, *callback_args, **default_kwargs)
        # Validate the response.
        if not isinstance(response, HttpResponse):
            raise ValueError, "The view %s.%s didn't return an HttpResponse object." % (self.__class__.__name__, callback.__name__)
        return response
    
    def render_to_response(self, request, template_name, context, **kwargs):
        """Renders the given template using the given context."""
        # Parse context variables.
        page = self.page
        breadcrumbs = request.breadcrumbs
        homepage = breadcrumbs[0]
        # Parse the main section.
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
        # Generate the context.
        base_context = {"page": page,
                        "title": page.title,
                        "short_title": page.short_title,
                        "browser_title": page.browser_title,
                        "meta_description": page.meta_description,
                        "meta_keywords": page.meta_keywords,
                        "robots_index": page.robots_index,
                        "robots_archive": page.robots_archive,
                        "robots_follow": page.robots_follow,
                        "content": self,
                        "breadcrumbs": self.breadcrumbs,
                        "homepage": homepage,
                        "is_homepage": (page == homepage),
                        "nav_primary": homepage.content.navigation,
                        "section": section,
                        "nav_secondary": nav_secondary,
                        "subsection": subsection,
                        "nav_tertiary": nav_tertiary}
        base_context.update(context)
        return render_to_response(template_name, base_context, template.RequestContext(request), **kwargs)
    
    @view("^$")
    def index(self, request):
        """Renders the content as a HTML page."""
        model = self.page.__class__
        model_name = model.__name__.lower()
        content_name = self.__class__.__name__.lower()
        opts = model._meta
        template_name = ("%s/%s/%s.html" % (opts.app_label, model_name, content_name),
                         "%s/%s.html" % (opts.app_label, content_name),
                         "%s.html" % (content_name),)
        return self.render_to_response(request, template_name, {})
        
    @view("^([a-zA-Z0-9_\-]+)/(.*)$", priority=-100)
    def dispatch_to_child(self, request, child_slug, path_info):
        """Dispatches the request to a child page."""
        page = self.page
        for child in page.children:
            if child.url_title == child_slug:
                return child.dispatch(request, path_info)
        raise Http404, "The %s '%s' does not have a child with a url title of '%s'" % (page.__class__.__name__.lower(), page, child_slug)
        
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

def get_add_permission(slug, model):
    """Generates the add permission codename for the given slug."""
    if slug == DEFAULT_CONTENT_SLUG:
        raise ValueError, "Base content model does not have an add permission."
    return u"add_%s_%s" % (slug, model.__name__.lower())


# Simple base content models.

class Content(ContentBase):
    
    """The default page content associated by default with all pages."""
    
    verbose_name_plural = "content"
    
    main = HtmlField("main content")      


class Redirect(ContentBase):
    
    """A redirect to another URL."""
    
    icon = settings.CMS_MEDIA_URL + "img/content-types/redirect.png"
    
    redirect_url = CharField(help_text="The URL where the user will be redirected.")
    
    