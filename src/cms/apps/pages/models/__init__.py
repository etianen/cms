"""Core models used by the CMS."""


import datetime

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.db import models
from django.db.models import Q

import optimizations

from cms.core import sitemaps
from cms.core.models.base import PageBase
from cms.core.models.managers import publication_manager
from cms.apps import historylinks
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

    parent = PageField(
        blank = True,
        null = True
    )

    order = models.PositiveIntegerField(editable=False)

    @optimizations.cached_property
    @publication_manager.getter
    def children(self):
        """The children of this page."""
        return list(Page.objects.filter(parent=self).order_by("order").iterator())
    
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
    
    content_type = models.ForeignKey(
        ContentType,
        editable = False,
        help_text="The type of page content.",
    )
    
    @optimizations.cached_property
    def content(self):
        """The associated content model for this page."""
        content_cls = ContentType.objects.get_for_id(self.content_type_id).model_class()
        content = content_cls._default_manager.get(page=self)
        content.page = self
        return content

    # Standard model methods.
    
    def get_absolute_url(self):
        """Generates the absolute url of the page."""
        if self.parent:
            return self.parent.get_absolute_url() + self.url_title + "/"
        return urlresolvers.get_script_prefix()
    
    def reverse(self, view_func, args, kwargs):
        """Performs a reverse URL lookup."""
        urlconf = ContentType.objects.get_for_id(self.content_type_id).model_class().urlconf
        return self.get_absolute_url() + urlresolvers.reverse(view_func, args=args, kwargs=kwargs, urlconf=urlconf, prefix="")
    
    def save(self, force_insert=False, force_update=False, using=None, user=None):
        """Saves the page."""
        super(Page, self).save(force_insert, force_update, using, user)
        self.__class__.objects.cache.put(self)
        
    def delete(self, using=None):
        """Deletes the page."""
        super(Page, self).delete(using)
        self.__class__.objects.cache.remove(self)
    
    class Meta:
        unique_together = (("parent", "url_title",),)
        ordering = ("order",)


historylinks.register(Page)


sitemaps.register(Page)


# Base content class.

def get_registered_content():
    """Returns a list of all registered content objects."""
    return [
        model for model in models.get_models()
        if issubclass(model, ContentBase) and not model._meta.abstract
    ]
    

class ContentBase(models.Model):
    
    """Base class for page content."""
    
    # This must be a 64 x 64 pixel image.
    icon = settings.STATIC_URL + "cms/img/content-types/content.png"

    # The heading that the admin places this content under.
    classifier = "content"

    # The urlconf used to power this content's views.
    urlconf = "cms.apps.pages.urls"
    
    # A fieldset definition. If blank, one will be generated.
    fieldsets = None
    
    page = models.OneToOneField(
        Page,
        primary_key = True,
        editable = False,
        related_name = "+",
    )
    
    def __unicode__(self):
        """Returns a unicode representation."""
        return u"Content for {0}.".format(self.page)
    
    class Meta:
        abstract = True