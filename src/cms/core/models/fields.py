"""Fields used by the page management application."""

from django.db import models

from cms.core.forms.widgets import HtmlWidget, NullBooleanWidget


class HtmlField(models.TextField):
    
    """A field that contains HTML data."""
    
    def formfield(self, **kwargs):
        """Returns a HtmlWidget."""
        kwargs["widget"] = HtmlWidget
        return super(HtmlField, self).formfield(**kwargs)
        

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
        "^cms\.core\.models\.fields\.HtmlField",
        "^cms\.core\.models\.fields\.NullBooleanField",
    ))