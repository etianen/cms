"""Models used by the static media management application."""


from django.core.files.storage import default_storage
from django.db import models


class Folder(models.Model):
    
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
    
    
def get_upload_path(instance, filename):
    """
    Generates the upload path for static media files.
    
    This will attempt to prevent filename mangling by prefixing the filename
    with a folder representing the version of the file that was uploaded.
    """
    folder_name = instance._meta.verbose_name_plural.replace(" ", "-")
    file_version = 1
    while True:
        upload_path = "uploads/%s/%i/%s" % (folder_name, file_version, filename)
        if not default_storage.exists(upload_path):
            return upload_path
        file_version += 1
    
    
class File(models.Model):
    
    """A static file."""
    
    title = models.CharField(max_length=200,
                             help_text="The title will be used as the default rollover text when this media is embedded in a web page.")
    
    last_modified = models.DateTimeField(auto_now=True,
                                         help_text="The date and time of when this media was last modified.")
    
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
    
