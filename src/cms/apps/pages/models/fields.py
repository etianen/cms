"""Fields used by the page management application."""


from django.db import models
from django.db.models.fields.related import ReverseSingleRelatedObjectDescriptor

from cms.apps.pages import content
from cms.core.models.base import PublishedModel
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
        if isinstance(instance, PublishedModel):
            with publication_manager.select_published(instance._select_published_active):
                return self.field.rel.to.objects.get_page(page_id)
        else:
            return self.field.rel.to.objects.get_page(page_id)
        

class PageField(models.ForeignKey):
    
    """A foreign key to a Page model."""
    
    def __init__(self, content_type=None, limit_choices_to=None, **kwargs):
        """Initializes the Page Field."""
        if isinstance(content_type, basestring):
            content_type = content.lookup(content_type)
        self.content_type = content_type
        # Generate the page filter.
        if content_type is not None:
            limit_choices_to = limit_choices_to or {}
            content_keys = tuple(cls.registration_key
                                 for cls in content.registered_content.values()
                                 if issubclass(cls, content_type))
            limit_choices_to.setdefault("content_type__in", content_keys)
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