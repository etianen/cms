"""Core models used by the CMS."""

from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.db import models
from django.db.models import Q
from django.utils.functional import cached_property
from django.utils import timezone

from cms import sitemaps
from cms.models.base import PageBase, OnlineBaseManager
from cms.apps import historylinks


def get_default_page_parent():
    """Returns the default page parent."""
    try:
        return Page.objects.all()[0]
    except IndexError:
        return None


class PageManager(OnlineBaseManager):
    
    """Manager for Page objects."""
    
    def select_published(self, queryset):
        """Selects only published pages."""
        queryset = super(PageManager, self).select_published(queryset)
        now = timezone.now()
        queryset = queryset.filter(Q(publication_date=None) | Q(publication_date__lte=now))
        queryset = queryset.filter(Q(expiry_date=None) | Q(expiry_date__gt=now))
        return queryset
    
    def get_homepage(self):
        """Returns the site homepage."""
        return self.prefetch_related("child_set__child_set").get(parent=None)


class Page(PageBase):

    """A page within the site."""
    
    objects = PageManager()
    
    # Hierarchy fields.

    parent = models.ForeignKey(
        "self",
        blank = True,
        null = True,
        default = get_default_page_parent,
        related_name = "child_set",
    )

    order = models.IntegerField(editable=False)
    
    @cached_property
    def children(self):
        """The child pages for this page."""
        children = []
        for child in self.child_set.all():
            child.parent = self
            children.append(child)
        return children
    
    @property
    def navigation(self):
        """The sub-navigation of this page."""
        return [child for child in self.children if child.in_navigation]
    
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

    # Content fields.
    
    content_type = models.ForeignKey(
        ContentType,
        editable = False,
        help_text="The type of page content.",
    )
    
    @cached_property
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
    icon = "pages/img/content.png"

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