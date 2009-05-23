"""Models used by the page management application."""


from django.conf import settings
from django.db import models

from cms.core import lookup
from cms.core.models import ContentModel
from cms.core.models import PublishedManager as BasePublishedManager
from cms.core.optimizations import cached_property
from cms.core.serializers import serializer


class PublishedManager(BasePublishedManager):
    
    """Manager that only returns published pages."""
    
    def get_query_set(self):
        """Returns all content that is published."""
        now = datetime.datetime.now()
        queryset = super(PublishedManager, self).get_query_set()
        queryset = queryset.filter(models.Q(publication_date=None) | models.Q(publication_date__lte=now))
        queryset = queryset.filter(models.Q(expiry_date=None) | models.Q(expiry_date__gt=now))
        return queryset


# Make a fast dict of content types.
PAGE_CONTENT_TYPES = dict([(slug, lookup.get_object(content_type))
                           for slug, content_type in settings.PAGE_CONTENT_TYPES])


def get_page_content_type(type):
    """Returns the names page content type."""
    return PAGE_CONTENT_TYPES[type]


class Page(ContentModel):
    
    """A page within the site."""
    
    # Manager classes.
    
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
    
    children = cached_property(get_children,
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
    
    published_children = cached_property(get_published_children,
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
    
    navigation = cached_property(get_navigation,
                                 doc="All the published children of this page in the site navigation.")
    
    # Content fields.
    
    type = models.CharField(max_length=20,
                            editable=False,
                            help_text="The type of page content.")
    
    content_data = models.TextField(editable=False,
                                    help_text="The encoded data of this page.")
    
    def get_content(self):
        """Returns the content object associated with this page."""
        content_cls = get_page_content_type(self.type)
        if self.content_data:
            content_data = serializer.deserialize(self.content_data)
        else:
            content_data = {}
        content = content_cls(self.type, self, content_data)
        return content

    def set_content(self, content):
        """Sets the content object for this page."""
        self.type = content.type
        self.content_data = serializer.serialize(content.content_data)
    
    content = cached_property(get_content,
                              set_content,
                              doc="The content object associated with this page.")
    
    class Meta:
        unique_together = (("parent", "url_title",),)
        
