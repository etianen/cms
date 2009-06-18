"""Models used by the static media management application."""


from django.core.files.storage import default_storage
from django.db import models


class Folder(models.Model):
    
    """
    A notional folder used to organise static media.
    
    This does not correspond to a physical folder on the disk.
    """
    
    name = models.CharField(max_length=100)
    
    def __unicode__(self):
        """Returns the name of the folder."""
        return self.name
    
    class Meta:
        ordering = ("name",)


class Media(models.Model):
    
    """
    Base class for all static media models.
    
    Subclasses must define a field called 'file' which must be a FileField or
    one of its subclasses.
    """
    
    title = models.CharField(max_length=100,
                             help_text="The title will be used as the default rollover text when this media is embedded in a web page.")
    
    size = models.PositiveIntegerField(editable=False,
                                       help_text="The size of this media, in bytes.")
    
    last_modified = models.DateTimeField(auto_now=True,
                                         help_text="The date and time of when this media was last modified.")
    
    folder = models.ForeignKey(Folder,
                               blank=True,
                               null=True,
                               help_text="Folders are used to help organise your media. They are not visible to users on your website.")
    
    keywords = models.CharField(max_length=1000,
                                blank=True,
                                null=True,
                                help_text="Keywords help narrow down results when you are searching for media. They are not visible to users on your website.")
    
    notes = models.TextField(blank=True,
                             null=True,
                             help_text="Notes are for your own reference, to help keep track of what this media is used for on your site. They are not visible to users on your website.")
    
    def save(self, *args, **kwargs):
        """Adds the associated metadata before saving this media."""
        self.size = self.file.size
        super(Media, self).save(*args, **kwargs)
    
    def get_absolute_url(self):
        """Generates the absolute URL of the image."""
        return self.file.url
    
    def __unicode__(self):
        """Returns the title of the media."""
        return self.title
    
    class Meta:
        abstract = True
        ordering = ("title",)
    
    
def get_upload_path(instance, filename):
    """
    Generates the upload path for static media files.
    
    This will attempt to prevent filename mangling by prefixing the filename
    with a folder representing the version of the file that was uploaded.
    """
    folder_name = instance._meta.verbose_name_plural.replace(" ", "-")
    file_version = 1
    while True:
        upload_path = "%s/%i/%s" % (folder_name, file_version, filename)
        if not default_storage.exists(upload_path):
            return upload_path
        file_version += 1
    
    
class File(Media):
    
    """A static file."""
    
    file = models.FileField(upload_to=get_upload_path)
    
    
class Image(Media):
    
    """A static image."""
    
    file = models.ImageField(upload_to=get_upload_path,
                             width_field="width",
                             height_field="height")
    
    width = models.PositiveSmallIntegerField(editable=False,
                                             help_text="The width of this image, in pixels.")
    
    height = models.PositiveSmallIntegerField(editable=False,
                                              help_text="The height of this image, in pixels.")
    
    