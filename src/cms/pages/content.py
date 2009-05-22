"""Some base page content types."""


from django import forms


class ContentField(object):
    
    """A field within a Content object."""
    
    form_field = forms.CharField
    
    widget = forms.TextInput
    
    def __init__(self, label=None, required=False, help_text=""):
        """"Initializes the ContentField."""
        self.label = label
        self.required = required
        self.help_text = help_text
    
    def contribute_to_class(self, cls, name):
        """Called automatically by the ContentMetaClass on class creation."""
        self.name = name
    
    def __get__(self, obj, cls=None):
        """Retrieves the value from the Content object."""
        if obj is None:
            return self
        try:
            return obj.content_data[self.name]
        except IndexError:
            raise AttributeError, self.name

    def __set__(self, obj, value):
        """Sets the value in the Content object."""
        obj.content_data[self.name] = value

    def __delete__(self, obj):
        """Removes the value from the Content object."""
        del obj.content_data[self.name]
        
    def get_default_attrs(self):
        """Returns the default attributes for a form field."""
        attrs = {"label": self.label,
                 "required": self.required,
                 "help_text": self.help_text,
                 "widget": self.widget}
        return attrs
        
    def get_formfield(self, **kwargs):
        """Returns a form field for this content field."""
        defaults = self.get_default_attrs()
        defaults.extend(kwargs)
        return self.form_field(**defaults)
           

class CharField(ContentField):
    
    """A simple character data field."""
    
    def __init__(self, label=None, max_length=100, **kwargs):
        """Initializes the CharField."""
        super(CharField, self).__init__(label, **kwargs)
        self.max_length = max_length
        
    def get_default_attrs(self):
        """Adds the max length to the default attributes."""
        attrs = super(CharField, self).get_default_attrs()
        attrs["max_length"] = self.max_length
        return attrs
    
    
class TextField(CharField):
    
    """A text data field."""
    
    widget = forms.Textarea
            
    
class ContentMetaClass(type):
    
    """Metaclass for Content objects."""
    
    def __new__(cls, name, bases, attrs):
        """Initializes the ContentMetaClass."""
        self = super(ContentMetaClass, cls).__new__(cls, name, bases, attrs)
        for key, value in attrs.items():
            if hasattr(value, "contribute_to_class"):
                value.contribute_to_class(cls, key)
        return self
                

class Content(object):
    
    """
    The base page content type.
    
    Subclasses should extend this with additional functionality.
    """
    
    __metaclass__ = ContentMetaClass
    
    def __init__(self, page, content_data):
        """Initializes the page content."""
        self.page = page
        self.content_data = content_data
        

class SimpleContent(Content):
    
    """A single column content page."""
    
    content = TextField()
    
    