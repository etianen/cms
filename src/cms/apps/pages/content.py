"""Pluggable page content, serialized to XML."""


import cStringIO, datetime
from xml.dom import minidom
from xml.sax.saxutils import XMLGenerator

from django import forms
from django.conf import settings
from django.contrib.admin.widgets import AdminTextInputWidget, AdminTextareaWidget
from django.db.models.options import get_verbose_name
from django.http import HttpResponse

from cms.apps.pages.forms import PageForm, HtmlWidget


class Field(object):
    
    """A field within a Content object."""
    
    creation_counter = 0
    
    form_field = forms.CharField
    
    def __init__(self, label=None, required=False, help_text=""):
        """"Initializes the Field."""
        self.label = label
        self.required = required
        self.help_text = help_text
        Field.creation_counter += 1
        self.creation_order = self.creation_counter
    
    def contribute_to_class(self, cls, name):
        """Called automatically by the ContentMetaClass on class creation."""
        self.name = name
    
    def __get__(self, obj, cls=None):
        """Retrieves the value from the Content object."""
        if obj is None:
            return self
        return obj.data.get(self.name, "")

    def __set__(self, obj, value):
        """Sets the value in the Content object."""
        obj.data[self.name] = value
        
    def get_formfield_attrs(self, obj):
        """Returns the default attributes for a form field."""
        initial = self.__get__(obj, obj.__class__)
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
    
    
class ContentMetaClass(type):
    
    """Metaclass for Content objects."""
    
    def __new__(cls, name, bases, attrs):
        """Initializes the ContentMetaClass."""
        self = super(ContentMetaClass, cls).__new__(cls, name, bases, attrs)
        self.fields = []
        for key, value in attrs.items():
            # Perform metaclass programming.
            if hasattr(value, "contribute_to_class"):
                value.contribute_to_class(cls, key)
            # Register fields.
            if isinstance(value, Field):
                self.fields.append(value)
        # Sort fields by creation order.
        self.fields.sort(lambda a, b: cmp(a.creation_order, b.creation_order))
        # Generate a verbose name, if required.
        if not "verbose_name" in attrs:
            verbose_name = get_verbose_name(name)
            setattr(self, "verbose_name", verbose_name)
        if not "verbose_name_plural" in attrs:
            self.verbose_name_plural = self.verbose_name + "s"
        return self
                

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
        
    # Model delegation methods.
    
    def get_navigation(self):
        """
        Generates the sub-navigation of the page.
        
        This is returned in the form of a dictionary of 'title' and 'url'.
        An option third item is 'navigation', which should be an iterable of
        sub navigation.
        """
        navigation_pages = self.page.get_published_children().filter(in_navigation=True)
        navigation = [{"title": page.short_title or page.title,
                       "url": page.get_absolute_url(),
                       "navigation": (entry for entry in page.navigation)}
                       for page in navigation_pages]
        return navigation
    
    def render_to_response(self, request, extra_context=None):
        """Generates a HttpResponse for this context."""
        context = {}
        context.update(extra_context or {})
        return HttpResponse("Hello World")
        
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
    
    