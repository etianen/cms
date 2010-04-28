"""Fields used by the page management application."""


from django.core.exceptions import ValidationError
from django.db import models

from cms.core.forms.widgets import HtmlWidget, NullBooleanWidget


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