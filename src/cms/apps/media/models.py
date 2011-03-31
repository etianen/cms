"""Models used by the static media management application."""


from django.db import models

from cms.core.files import get_upload_path
from cms.core.models import AuditBase


class Folder(AuditBase):
    
    """
    A notional folder used to organise static media.
    
    This does not correspond to a physical folder on the disk.
    """
    
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        """Returns the name of the folder."""
        return self.name
    
    class Meta:
        ordering = ("name",)
    
    
class File(AuditBase):
    
    """A static file."""
    
    title = models.CharField(max_length=200,
                             help_text="The title will be used as the default rollover text when this media is embedded in a web page.")
    
    folder = models.ForeignKey(Folder,
                               blank=True,
                               null=True,
                               help_text="Folders are used to help organise your media. They are not visible to users on your website.")
    
    file = models.FileField(upload_to=get_upload_path,
                            max_length=200)
    
    def get_absolute_url(self):
        """Generates the absolute URL of the image."""
        return self.file.url
    
    def __unicode__(self):
        """Returns the title of the media."""
        return self.title
    
    class Meta:
        ordering = ("title",)


IMAGE_FILTER = {"file__iregex": ur"^.+\.(png|gif|jpg|jpeg)$"} 
        
class ImageRefField(models.ForeignKey):
    
    """A foreign key to a File, constrained to only select image files."""
    
    def __init__(self, **kwargs):
        kwargs["to"] = File
        kwargs["limit_choices_to"] = IMAGE_FILTER
        kwargs.setdefault("related_name", "+")
        kwargs.setdefault("on_delete", models.PROTECT)
        super(ImageRefField, self).__init__(**kwargs)
        
        
# Register custom fields with South.

try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    # Rules for ImageRefField.
    add_introspection_rules((), ("^cms\.apps\.media\.models\.ImageRefField",))