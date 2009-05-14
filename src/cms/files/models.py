"""Models used by the file management application."""


from django.db import models


class Category(models.Model):
    
    """A category used to clasify files."""
    
    name = models.CharField(max_length=100)
    
    def __unicode__(self):
        """Returns the name of the category."""
        return self.name
    
    class Meta:
        verbose_name_plural = "categories"
        ordering = ("name",)
        
        
class File(models.Model):
    
    """An uploaded file."""
    
    title = models.CharField(max_length=100)
    
    category = models.ForeignKey(Category,
                                 blank=True,
                                 null=True,
                                 help_text="Use categories to help keep your files organised.")
    
    file = models.FileField(max_length=1000,
                            upload_to="files/%Y/%m/%d")
    
    def __unicode__(self):
        """Returns the title of the file."""
        return self.title
    
    class Meta:
        ordering = ("title",)
        
        