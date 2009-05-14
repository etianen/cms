"""Models used by the page management application."""


from django.db import models

from cms.core.models import Content


class Page(Content):
    
    """A page within the site."""
    
    # Base fields.
    
    url_title = models.SlugField("URL title")
    
    # Hierarchy fields.
    
    parent = models.ForeignKey("self",
                               blank=True,
                               null=True)
    
    order = models.PositiveSmallIntegerField(unique=True,
                                             editable=False,
                                             blank=True,
                                             null=True)
    
    def get_children(self):
        """
        Returns all the children of this page, regardless of their publication
        state.
        """
        return Page.objects.order_by("order", "id")
    
    children = property(get_children,
                        doc="All the children of this page, regardless of their publication state.")
    
    def get_published_children(self):
        """Returns all the published children of this page."""
        return Page.published_objects.order_by("order", "id")
    
    published_children = property(get_published_children,
                                  doc="All the published children of this page.")
    
    # Navigation fields.
    
    short_title = models.CharField(max_length=100,
                                   blank=True,
                                   null=True,
                                   help_text="A shorter version of the title that will be used in site navigation. Leave blank to use the full-length title.")

    in_navigation = models.BooleanField("add to navigation",
                                        default=True,
                                        help_text="Uncheck this box to remove this content from the site navigation.")
    
    def get_navigation(self):
        """
        Returns all published children of this page in the site navigation.
        """
        return self.get_published_children().filter(in_navigation=True)
    
    navigation = property(get_navigation,
                          doc="All the published children of this page in the site navigation.")
    
    class Meta:
        unique_together = (("parent", "url_title",),)
        
        