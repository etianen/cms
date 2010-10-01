"""Models used by the static media management application."""


from django.db import models

from cms.core.files import get_upload_path


class Folder(models.Model):
    
    """
    A notional folder used to organise static media.
    
    This does not correspond to a physical folder on the disk.
    """
    
    name = models.CharField(max_length=200)
    
    date_created = models.DateTimeField(auto_now_add=True)
    
    date_modified = models.DateTimeField("last modified",
                                         auto_now=True,)
    
    def __unicode__(self):
        """Returns the name of the folder."""
        return self.name
    
    class Meta:
        ordering = ("name",)
    
    
class File(models.Model):
    
    """A static file."""
    
    title = models.CharField(max_length=200,
                             help_text="The title will be used as the default rollover text when this media is embedded in a web page.")
    
    date_created = models.DateTimeField(auto_now_add=True)
    
    date_modified = models.DateTimeField("last modified",
                                         auto_now=True,)
    
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
        
        
class ImageRefField(models.ForeignKey):
    
    """A foreign key to a File, constrained to only select image files."""
    
    def __init__(self, **kwargs):
        kwargs["to"] = File
        kwargs["limit_choices_to"] = {"file__iregex": ur"^.+\.(png|gif|jpg|jpeg)$"}
        super(ImageRefField, self).__init__(**kwargs)