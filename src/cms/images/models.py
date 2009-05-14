"""Models used by the image management application."""


from django.db import models


class Category(models.Model):
    
    """A category used to clasify images."""
    
    name = models.CharField(max_length=100)
    
    def __unicode__(self):
        """Returns the name of the category."""
        return self.name
    
    class Meta:
        verbose_name_plural = "categories"
        ordering = ("name",)
        
        
class Image(models.Model):
    
    """An uploaded image."""
    
    title = models.CharField(max_length=100)
    
    category = models.ForeignKey(Category,
                                 blank=True,
                                 null=True,
                                 help_text="Use categories to help keep your images organised.")
    
    image = models.ImageField(max_length=1000,
                              width_field="width",
                              height_field="height",
                              upload_to="images/%Y/%m/%d")
    
    width = models.PositiveSmallIntegerField(editable=False)
    
    height = models.PositiveSmallIntegerField(editable=False)
    
    def __unicode__(self):
        """Returns the title of the image."""
        return self.title
    
    class Meta:
        ordering = ("title",)
        
        