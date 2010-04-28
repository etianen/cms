"""Field definitions for content models."""


import os

from django import forms
from django.core.files.images import get_image_dimensions
from django.core.files.storage import default_storage
from django.contrib.admin.widgets import AdminTextInputWidget, AdminTextareaWidget, AdminFileWidget
from django.utils.text import capfirst

from cms.core.forms.widgets import HtmlWidget
from cms.core.optimizations import cached_getter


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
    
    
class BooleanField(Field):
    
    """A field that holds a boolean value."""
    
    form_field = forms.BooleanField
    
    def get_formfield_attrs(self, obj):
        """Sets a custom widget default attributes."""
        attrs = super(BooleanField, self).get_formfield_attrs(obj)
        attrs["widget"] = forms.CheckboxInput
        return attrs
    
    def serialize(self, value):
        """Converts the value into a unicode string."""
        return unicode(int(value))
    
    def deserialize(self, value):
        """Converts the value from a unicode string into a Python object."""
        if value == "":
            return None
        return bool(int(value))
    
    
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
        
        
class ContentFile(object):
    
    """A file associated with a content object."""
    
    def __init__(self, name, storage):
        """Initializes the ContentFile."""
        self.name = name
        self.storage = storage
        
    def get_url(self):
        """Returns the URL of the file."""
        return self.storage.url(self.name)
    
    url = property(get_url,
                   doc="The URL of the file")
    
    def get_path(self):
        """Returns the path of the file on disk."""
        return self.storage.path(self.name)
    
    path = property(get_path,
                    doc="The path of the file on disk.")
    
    def get_size(self):
        """Returns the size of the file on disk, in bytes."""
        return self.storage.size(self.name)
        
    size = property(get_size,
                    doc="The size of the file on disk, in bytes.")
    
    def __unicode__(self):
        """Returns the name of the file."""
        return self.name
    
    
class ContentImageFile(ContentFile):
    
    """An image file associated with a content object."""
    
    @cached_getter
    def get_dimensions(self):
        """Returns a tuple of the dimensions of the image, in pixels."""
        return get_image_dimensions(self.path)
    
    dimensions = property(get_dimensions,
                          doc="A tuple of the dimensions of the image, in pixels.")
    
    def get_width(self):
        """Returns the width of the image, in pixels."""
        return self.dimensions[0]
    
    width = property(get_width,
                     doc="The width of the image, in pixels.")
    
    def get_height(self):
        """Returns the height of the image in pixels."""
        return self.dimensions[1]
    
    height = property(get_height,
                      doc="The height of the image, in pixels.")
        

class FileField(Field):
    
    """A field that holds a path to a file on disk."""
    
    form_field = forms.FileField
        
    file_class = ContentFile
        
    def __init__(self, label=None, upload_to=None, storage=None, **kwargs):
        """Initializes the FileField."""
        self.upload_to = upload_to
        self.storage = storage or default_storage
        super(FileField, self).__init__(label, **kwargs)
        
    def contribute_to_class(self, cls, name):
        """Sets the default upload path."""
        super(FileField, self).contribute_to_class(cls, name)
        self.upload_to = self.upload_to or cls.verbose_name_plural.replace(" ", "-")
        
    def get_formfield_attrs(self, obj):
        """Changes the widget of the form field to an admin file widget."""
        attrs = super(FileField, self).get_formfield_attrs(obj)
        attrs["widget"] = AdminFileWidget
        return attrs
    
    def serialize(self, value):
        """Serializes given value as a unicode string."""
        # Compatible files are easy.
        if isinstance(value, ContentFile) and value.storage == self.storage:
            return value.name
        # Copy the data across.
        filename = os.path.basename(value.name)
        destination = self.upload_to + "/" + filename
        value.open()
        return self.storage.save(destination, value)
    
    def deserialize(self, value):
        """Converts the value from a unicode string into a Python object."""
        if value == "":
            return None
        return self.file_class(value, self.storage)
        
        
class ImageField(FileField):
    
    """A field that holds a path to an image on disk."""
    
    form_field = forms.ImageField

    file_class = ContentImageFile
    
    
class ModelField(Field):
    
    """A field that holds a reference to a model."""
    
    form_field = forms.ModelChoiceField
    
    def __init__(self,  queryset, label=None, **kwargs):
        """Initializes the ModelField."""
        self.queryset = queryset
        super(ModelField, self).__init__(label, **kwargs)
    
    def get_formfield_attrs(self, obj):
        """Primes the choices in the form field."""
        initial = self.get_value_from_object(obj)
        attrs = super(ModelField, self).get_formfield_attrs(obj)
        attrs["queryset"] = self.queryset.all()
        attrs["initial"] = unicode(initial and initial.pk or "")
        del attrs["widget"]
        return attrs
    
    def serialize(self, value):
        """Serializes given value as a unicode string."""
        return unicode(value.pk)
    
    def deserialize(self, value):
        """Converts the value from a unicode string into a Python object."""
        if value == "":
            return None
        model = self.queryset.model
        try:
            return self.queryset.model.objects.get(pk=value)
        except model.DoesNotExist:
            return None
        except ValueError:
            # Be resilient to bad data.
            return None
    