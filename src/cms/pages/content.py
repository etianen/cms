"""Pluggable page content, serialized to XML."""


from django import forms

from cms.pages.widgets import HtmlWidget


class ContentField(object):
    
    """A field within a Content object."""
    
    form_field = forms.CharField
    
    widget = forms.TextInput
    
    creation_counter = 0
    
    def __init__(self, label=None, required=False, help_text=""):
        """"Initializes the ContentField."""
        self.label = label
        self.required = required
        self.help_text = help_text
        self.creation_counter += 1
        self.creation_order = self.creation_counter
    
    def contribute_to_class(self, cls, name):
        """Called automatically by the ContentMetaClass on class creation."""
        self.name = name
    
    def __get__(self, obj, cls=None):
        """Retrieves the value from the Content object."""
        if obj is None:
            return self
        return obj.content_data.get(self.name, "")

    def __set__(self, obj, value):
        """Sets the value in the Content object."""
        obj.content_data[self.name] = value

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
           

class CharField(ContentField):
    
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
    
    widget = forms.Textarea
            
    
class HtmlField(TextField):
    
    """A HTML rich text field."""
    
    widget = HtmlWidget
    
    
class ContentMetaClass(type):
    
    """Metaclass for Content objects."""
    
    def __new__(cls, name, bases, attrs):
        """Initializes the ContentMetaClass."""
        self = super(ContentMetaClass, cls).__new__(cls, name, bases, attrs)
        self.fields = []
        for key, value in attrs.items():
            if hasattr(value, "contribute_to_class"):
                value.contribute_to_class(cls, key)
            if isinstance(value, ContentField):
                self.fields.append(value)
        self.fields.sort(lambda a, b: cmp(a.creation_order, b.creation_order))
        return self
                

class Content(object):
    
    """
    The base page content type.
    
    Subclasses should extend this with additional functionality.
    """
    
    __metaclass__ = ContentMetaClass
    
    def __init__(self, type, page, content_data):
        """Initializes the page content."""
        self.type = type
        self.page = page
        self.content_data = content_data
        
    def get_form(self):
        """Returns a form used to edit this Content."""
        form_attrs = dict([(field.name, field.get_formfield(self))
                           for field in self.fields])
        Form = type("%sForm" % self.__class__.__name__, (forms.ModelForm,), form_attrs)
        return Form
    
    def get_field_names(self):
        """Returns a list of all the named fields in this Content."""
        fields = [field.name for field in self.fields]
        return fields
    
    def get_fieldsets(self):
        """Returns the fieldsets used to lay out the content form."""
        field_names = self.get_field_names()
        return (("Page content", {"fields": field_names}),)
        

class SimpleContent(Content):
    
    """A single column content page."""
    
    content = HtmlField()
    
    