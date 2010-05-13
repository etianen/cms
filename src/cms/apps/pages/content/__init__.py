"""Pluggable page content, serialized to XML."""


import cStringIO, imp, weakref
from xml.dom import minidom
from xml.sax.saxutils import XMLGenerator

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.serializers.xml_serializer import getInnerText
from django.db.models.options import get_verbose_name

from cms.apps.pages.forms import PageForm
from cms.apps.pages.content.fields import Field, CharField, TextField, HtmlField, ChoiceField, URLField, EmailField, IntegerField, PositiveIntegerField, FileField, ImageField, ModelField, BooleanField  # @UnusedImport
    

# Known content classes.
registered_content = weakref.WeakValueDictionary()


class ContentRegistrationError(Exception):
    
    """Exception raised when content registration goes astray.""" 


def lookup(slug):
    """Looks up the given content type by type slug."""
    try:
        return registered_content[slug]
    except KeyError:
        raise ContentRegistrationError, "No content type is registered under '%s'." % slug
    
    
class ContentMetaClass(type):
    
    """Metaclass for Content objects."""
    
    def __init__(self, name, bases, attrs):
        """Initializes the ContentMetaClass."""
        super(ContentMetaClass, self).__init__(name, bases, attrs)
        self.fields = []
        for attr_name in dir(self):
            value = getattr(self, attr_name)
            # Perform metaclass programming.
            if hasattr(value, "contribute_to_class"):
                value.contribute_to_class(self, attr_name)
            # Register fields.
            if isinstance(value, Field):
                self.fields.append(value)
        # Sort fields by creation order.
        self.fields.sort(lambda a, b: cmp(a.creation_order, b.creation_order))
        # Generate a verbose name, if required.
        if not "verbose_name" in attrs:
            verbose_name = get_verbose_name(name)
            self.verbose_name = verbose_name
        if not "verbose_name_plural" in attrs:
            self.verbose_name_plural = self.verbose_name + "s"
        # Find the app_label of the content.
        if not "app_label" in attrs:
            module_name = attrs.get("__module__", "")
            module_parts = module_name.rsplit(".", 2)
            if len(module_parts) == 3 and module_parts[2] == "content":
                self.app_label = module_parts[1]
            else:
                raise ImproperlyConfigured, "The content class '%s' was not located in the content.py file of your application. Please specify an app_label for '%s'" % (name, name)
        # Auto-register the content.
        if not "registration_key" in attrs:
            self.registration_key = "%s.%s" % (self.app_label, name)
        if not "abstract" in attrs:
            self.abstract = False
        if not "use_as_default" in attrs:
            self.use_as_default = False
        if not "use_as_base" in attrs:
            self.use_as_base = False
        if not self.abstract:
            # Add to registration dictionary.
            if self.registration_key in registered_content:
                raise ContentRegistrationError, "A content class has already been registered under the key %s" % self.registration_key
            registered_content[self.registration_key] = self
            # Check if content is default.
            if self.use_as_default:
                global DefaultContent
                DefaultContent = self
            # Check if content is base.
            if self.use_as_base:
                global BaseContent
                BaseContent = self
        
        
class Content(object):
    
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
    
    # If true, then this will be used as the base class for all built-in CMS apps.
    use_as_base = False
    
    # If true, then this will be the default content for newly-created pages.
    use_as_default = False  
    
    # The urlconf used to power this content's views.
    urlconf = "cms.apps.pages.urls"
    
    def __init__(self, page):
        """
        Initializes the page content.
        
        If page is None, then an unbound content object is created.  Not all
        methods will work in an unbound content object, but it is fine for
        generating form fields used by the admin interface.
        """
        self.page = page
        if page and page.content_data:
            self._set_serialized_data(page.content_data)
        else:
            self.data = {}
        
    # Content serialization methods.
        
    def _get_serialized_data(self):
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
    
    def _set_serialized_data(self, serialized_data):
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


BaseContent = None
    
DefaultContent = None
    

# Permissions control.

def get_add_permission(slug):
    """Generates the add permission codename for the given slug."""
    if slug == DefaultContent.registration_key:
        raise ValueError, "Base content model does not have an add permission."
    return u"add_%s_page" % slug.lower().replace(".", "_")


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