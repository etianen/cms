"""Fields used by the page management application."""

from django.db import models

from cms.forms import HtmlWidget


class HtmlField(models.TextField):
    
    """A field that contains HTML data."""
    
    def formfield(self, **kwargs):
        """Returns a HtmlWidget."""
        kwargs["widget"] = HtmlWidget
        return super(HtmlField, self).formfield(**kwargs)
        
        
# Register custom fields with South.

try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    # Simple rules for HtmlField.
    add_introspection_rules((), (
        "^cms\.models\.fields\.HtmlField",
    ))