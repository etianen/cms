"""Models used by the page management application."""


from django.db import models

from cms.core.models import Content
from cms.core.models import PublishedManager as BasePublishedManager


class PublishedManager(BasePublishedManager):
    
    """Manager that only returns published pages."""
    
    def get_query_set(self):
        """Returns all content that is published."""
        now = datetime.datetime.now()
        queryset = super(PublishedManager, self).get_query_set()
        queryset = queryset.filter(models.Q(publication_date=None) | models.Q(publication_date__lte=now))
        queryset = queryset.filter(models.Q(expiry_date=None) | models.Q(expiry_date__gt=now))
        return queryset


class Page(Content):
    
    """A page within the site."""
    
    objects = models.Manager()
    
    published_objects = PublishedManager()
    
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
        return Page.objects.filter(parent=self).order_by("order", "id")
    
    children = property(get_children,
                        doc="All the children of this page, regardless of their publication state.")
    
    # Publication fields.
    
    publication_date = models.DateTimeField(blank=True,
                                            null=True,
                                            help_text="The date that this page will appear on the website.  Leave this blank to immediately publish this page.")
    
    expiry_date = models.DateTimeField(blank=True,
                                       null=True,
                                       help_text="The date that this page will be removed from the website.  Leave this blank to never expire this page.")

    def get_published_children(self):
        """Returns all the published children of this page."""
        return Page.published_objects.filter(parent=self).order_by("order", "id")
    
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
        
        