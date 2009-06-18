"""Pluggable page content, serialized to XML."""


import imp

from django import forms
from django.conf import settings
from django.contrib.admin.widgets import AdminTextInputWidget, AdminTextareaWidget
from django.db.models.options import get_verbose_name

from cms.apps.pages.forms import PageForm
from cms.apps.pages.widgets import HtmlWidget


class Field(object):
    
    """A field within a Content object."""
    
    form_field = forms.CharField
    
    widget = AdminTextInputWidget
    
    creation_counter = 0
    
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

    def get_default_attrs(self, obj):
        """Returns the default attributes for a form field."""
        initial = self.__get__(obj, obj.__class__)
        attrs = {"label": self.label,
                 "required": self.required,
                 "help_text": self.help_text,
                 "widget": self.widget,
                 "initial": initial}
        return attrs
        
    def get_formfield(self, obj, **kwargs):
        """Returns a form field for this content field."""
        defaults = self.get_default_attrs(obj)
        defaults.update(kwargs)
        return self.form_field(**defaults)
           

class CharField(Field):
    
    """A simple character data field."""
    
    def __init__(self, label=None, max_length=100, **kwargs):
        """Initializes the CharField."""
        super(CharField, self).__init__(label, **kwargs)
        self.max_length = max_length
        
    def get_default_attrs(self, obj):
        """Adds the max length to the default attributes."""
        attrs = super(CharField, self).get_default_attrs(obj)
        attrs["max_length"] = self.max_length
        return attrs
    
    
class TextField(CharField):
    
    """A text data field."""
    
    widget = AdminTextareaWidget
            
    
class HtmlField(TextField):
    
    """A HTML rich text field."""
    
    widget = HtmlWidget
    
    
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
        return self
                

class Content(object):
    
    """
    The base page content type.
    
    Subclasses should extend this with additional functionality.
    """
    
    __metaclass__ = ContentMetaClass
    
    # This must be a 64 x 64 pixel image.
    icon = settings.CMS_MEDIA_URL + "img/content-types/content.png"
    
    def __init__(self, page, data):
        """Initializes the page content."""
        self.page = page
        self.data = data
        
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
        

def autodiscover():
    """
    Searches all installed applications for content classes.
    
    All installed applications are checked for a content.py module.  If present,
    it is imported.
    """
    for app in settings.INSTALLED_APPS:
        try:
            app_path = __import__(app, {}, {}, [app.split('.')[-1]]).__path__
        except AttributeError:
            continue
        try:
            imp.find_module("content", app_path)
        except ImportError:
            continue
        __import__("%s.content" % app)
    
    
