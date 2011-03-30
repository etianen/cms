"""Models used by the history links service."""

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.db import models


class HistoryLinkManager(models.Manager):
    
    """Manager for HistoryLink models."""
    
    def create_for_obj(self, obj):
        """
        Creates a link for the given object.
        
        Returns a tuple of (created, historylink), similar to that returned by the
        QuerySet.get_or_create() method.
        """
        path = obj.get_absolute_url()
        content_type = ContentType.objects.get_for_model(obj)
        # Get the history link.
        try:
            link = HistoryLink.objects.get(path=path)
        except HistoryLink.DoesNotExist:
            link = HistoryLink(path=path)
        # Save if it has changed.
        if link.object_id != unicode(obj.id) and link.content_type_id != content_type.id:
            link.object = obj
            link.save()
            return True, link
        return False, link


class HistoryLink(models.Model):
    
    """A link to a moved / deleted model."""
    
    objects = HistoryLinkManager()
    
    date_created = models.DateTimeField(
        auto_now_add = True
    )
    
    date_modified = models.DateTimeField(
        auto_now = True
    )
    
    path = models.CharField(
        max_length = 255,
        unique = True,
    )
    
    content_type = models.ForeignKey(ContentType)
    
    object_id = models.TextField()
    
    object = GenericForeignKey()
    
    def __unicode__(self):
        """Returns a unicode representation."""
        return self.path