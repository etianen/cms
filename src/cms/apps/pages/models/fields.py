"""Fields used by the page management application."""


from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.fields.related import ReverseSingleRelatedObjectDescriptor

from cms.apps.pages.forms import HtmlWidget, NullBooleanWidget


class PageDescriptor(ReverseSingleRelatedObjectDescriptor):
    
    """A descriptor used to access referenced Page models."""
    
    def __get__(self, instance, instance_type=None):
        """Accesses the related page."""
        if instance is None:
            raise AttributeError, "%s must be accessed via instance" % self.field.name
        page_id = getattr(instance, self.field.attname)
        # Allow NULL values.
        if page_id is None:
            if self.field.null:
                return None
            raise self.field.rel.to.DoesNotExist
        # Access the page.
        return self.field.rel.to.objects.get_by_id(page_id)
        

class PageField(models.ForeignKey):
    
    """A foreign key to a Page model."""
    
    def __init__(self, content_type=None, limit_choices_to=None, **kwargs):
        """Initializes the Page Field."""
        self.content_type = content_type
        # Generate the page filter.
        if content_type is not None:
            limit_choices_to = limit_choices_to or {}
            limit_choices_to.setdefault("content_type", content_type)
        # Initialize the PageField.
        super(PageField, self).__init__(to="pages.Page", limit_choices_to=limit_choices_to, default=self.get_default, **kwargs)
        
    def get_default(self):
        """Returns the default page."""
        try:
            return self.rel.to._default_manager.filter(**self.rel.limit_choices_to)[0].pk
        except IndexError:
            return None
        
    def contribute_to_class(self, cls, name):
        """Sets the PageDescriptor on the class."""
        super(PageField, self).contribute_to_class(cls, name)
        setattr(cls, self.name, PageDescriptor(self))


class HtmlField(models.TextField):
    
    """A field that contains HTML data."""
    
    def formfield(self, **kwargs):
        """Returns a HtmlWidget."""
        kwargs["widget"] = HtmlWidget
        return super(HtmlField, self).formfield(**kwargs)
    
    
class EnumField(models.PositiveSmallIntegerField):
    
    """
    A field for storing integer representations of a number of string choices.
    
    Choices should be specified as a 3-tuple of integer_id, string and label.
    """
    
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, *args, **kwargs):
        """Initializes the EnumField."""
        enums = kwargs.get("choices", ())
        if not enums:
            raise ValueError, "You must specify at least one choice for EnumFields."
        # Generate the expected choice format.
        kwargs["choices"] = tuple((string, label) for id, string, label in enums)
        super(EnumField, self).__init__(*args, **kwargs)
        self._id_lookup = dict((id, string) for id, string, label in enums)
        self._string_lookup = dict((string, id) for id, string, label in enums)
        
    def to_python(self, value):
        """Converts the given value to the string."""
        if value is None:
            return value
        # Allow valid enum values.
        if isinstance(value, basestring):
            if value in self._string_lookup:
                return value
            else:
                raise ValidationError, "'%s' is not a valid enum value." % value
        # Allow valid enum ids.
        if isinstance(value, int):
            try:
                return self._id_lookup[value]
            except KeyError:
                raise ValidationError, "'%s' is not a valid enum id." % value
        # Only basestrings and ints are allowed.
        raise ValidationError, "'%s' should be a basestring or an int." % value
        
    def get_db_prep_value(self, value):
        """Converts the given value to an integer."""
        if value is None:
            return value
        # Allow valid enum ids.
        if isinstance(value, int):
            if value in self._id_lookup:
                return value
            else:
                raise ValidationError, "'%s' is not a valid enum id." % value
        # Allow valid enum values.
        if isinstance(value, basestring):
            try:
                return self._string_lookup[value]
            except KeyError:
                raise ValidationError, "'%s' is not a valid enum value." % value
        # Only basestrings and ints are allowed.
        raise ValidationError, "'%s' should be a basestring or an int." % value 
        

class NullBooleanField(models.NullBooleanField):
    
    """A null boolean field that has a blank choice instead of 'maybe',"""
    
    def formfield(self, **kwargs):
        """Generates the form field."""
        defaults = {"widget": NullBooleanWidget}
        defaults.update(kwargs)
        return super(NullBooleanField, self).formfield(**defaults)
    

# Register custom fields with South.

try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    # Simple rules for HtmlField and NullBooleanField.
    add_introspection_rules((), (
        "^cms\.apps\.pages\.models\.fields\.HtmlField",
        "^cms\.apps\.pages\.models\.fields\.NullBooleanField",
        "^cms\.apps\.pages\.models\.fields\.PageField",
        "^cms\.apps\.pages\.models\.fields\.EnumField",
    ))    