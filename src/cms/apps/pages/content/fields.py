"""Field definitions for content models."""


from django import forms
from django.contrib.admin.widgets import AdminTextInputWidget, AdminTextareaWidget
from django.utils.text import capfirst

from cms.apps.pages.forms import HtmlWidget


class Field(object):
    
    """A field within a Content object."""
    
    creation_counter = 0
    
    form_field = forms.CharField
    
    def __init__(self, label=None, required=True, default=None, help_text=""):
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
    
    def __init__(self, label=None, max_length=200, **kwargs):
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
        if value == "":
            return None
        return int(value)
    
    
class PositiveIntegerField(IntegerField):
    
    """A field that only holds positive integer numbers."""
    
    def __init__(self, label=None, max_value=None, **kwargs):
        """Initializes the PositiveIntegerField."""
        super(PositiveIntegerField, self).__init__(label, 0, max_value, **kwargs)
        
        