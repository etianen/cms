"""Core models used by the CMS."""


import datetime

from django.core import urlresolvers
from django.db import models
from django.db.models import Q

from cms.core import sitemaps
from cms.core.models.base import PageBase
from cms.core.models.managers import publication_manager
from cms.core.optimizations import cached_getter, cached_setter
from cms.apps.pages import content
from cms.apps.pages.models.managers import PageManager
from cms.apps.pages.models.fields import PageField


class Page(PageBase):

    """A page within the site."""

    objects = PageManager()
    
    @classmethod
    def select_published(cls, queryset):
        """Selects only published pages."""
        queryset = super(Page, cls).select_published(queryset)
        now = datetime.datetime.now()
        queryset = queryset.filter(Q(publication_date=None) | Q(publication_date__lte=now))
        queryset = queryset.filter(Q(expiry_date=None) | Q(expiry_date__gt=now))
        return queryset
    
    # Base fields.
    
    def __init__(self, *args, **kwargs):
        """"Initializes the Page."""
        super(Page, self).__init__(*args, **kwargs)
        if self.id:
            self.__class__.objects.cache.put(self)
    
    # Hierarchy fields.

    parent = PageField(blank=True,
                       null=True)

    order = models.PositiveIntegerField(editable=False)

    @property
    @cached_getter
    @publication_manager.getter
    def children(self):
        """The children of this page."""
        return Page.objects.filter(parent=self).order_by("order")
    
    @property
    def navigation(self):
        """The sub-navigation of this page."""
        return [child for child in super(Page, self).navigation if child.in_navigation]
    
    # Publication fields.
    
    publication_date = models.DateTimeField(blank=True,
                                            null=True,
                                            help_text="The date that this page will appear on the website.  Leave this blank to immediately publish this page.")

    expiry_date = models.DateTimeField(blank=True,
                                       null=True,
                                       help_text="The date that this page will be removed from the website.  Leave this blank to never expire this page.")

    # Navigation fields.

    in_navigation = models.BooleanField("add to navigation",
                                        default=True,
                                        help_text="Uncheck this box to remove this content from the site navigation.")

    permalink = models.SlugField(blank=True,
                                 help_text="A unique identifier for this page.  This will be set by your design team in order to link to this page from any custom templates they write.")

    # Content fields.
    
    content_type = models.CharField(max_length=100,
                                    editable=False,
                                    db_index=True,
                                    help_text="The type of page content.")

    content_data = models.TextField(editable=False,
                                    help_text="The encoded data of this page.")
    
    @cached_getter
    def get_content(self):
        """Returns the content object associated with this page."""
        if not self.content_type:
            return None
        content_cls = content.lookup(self.content_type)
        content_instance = content_cls(self)
        return content_instance

    @cached_setter(get_content)
    def set_content(self, content):
        """Sets the content object for this page."""
        self.content_data = content._get_serialized_data()

    content = property(get_content,
                       set_content,
                       doc="The content object associated with this page.")

    # Standard model methods.
    
    def get_absolute_url(self):
        """Generates the absolute url of the page."""
        if self.parent:
            return self.parent.get_absolute_url() + self.url_title + "/"
        return urlresolvers.get_script_prefix()
    
    def reverse(self, view_func, *args, **kwargs):
        """Performs a reverse URL lookup."""
        urlconf = content.lookup(self.content_type).urlconf
        return self.get_absolute_url() + urlresolvers.reverse(view_func, args=args, kwargs=kwargs, urlconf=urlconf, prefix="")
    
    def save(self, *args, **kwargs):
        """Saves the page."""
        super(Page, self).save(*args, **kwargs)
        self.__class__.objects.cache.put(self)
        
    def delete(self, *args, **kwargs):
        """Deletes the page."""
        super(Page, self).delete(*args, **kwargs)
        self.__class__.objects.cache.remove(self)
    
    class Meta:
        unique_together = (("parent", "url_title",),)
        ordering = ("order",)


class PageSitemap(sitemaps.PageBaseSitemap):
    
    """Sitemap for page models."""
    
    model = Page
    
    
sitemaps.registered_sitemaps["pages"] = PageSitemap