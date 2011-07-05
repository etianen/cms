"""Fields used by the page management application."""


from django.db import models
from django.db.models.fields.related import ReverseSingleRelatedObjectDescriptor

from cms.core.models.base import PublishedBase
from cms.core.models.managers import publication_manager


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
        if isinstance(instance, PublishedBase):
            with publication_manager.select_published(instance._select_published_active):
                return self.field.rel.to.objects.get_by_id(page_id)
        else:
            return self.field.rel.to.objects.get_by_id(page_id)
        

class PageField(models.ForeignKey):
    
    """A foreign key to a Page model."""
    
    def __init__(self, **kwargs):
        """Initializes the Page Field."""
        kwargs.setdefault("to", "pages.Page")
        super(PageField, self).__init__(**kwargs)
        
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
        
        
# Register custom fields with South.

try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    # Simple rules for HtmlField and NullBooleanField.
    add_introspection_rules((), (
        "^cms\.apps\.pages\.models\.fields\.PageField",
    ))