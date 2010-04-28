"""Core models used by the CMS."""


import datetime

from django.core import urlresolvers
from django.db import models
from django.db.models import Q

from cms.core import sitemaps
from cms.core.models.base import PageBase
from cms.core.optimizations import cached_getter, cached_setter
from cms.apps.pages import content
from cms.apps.pages.models.managers import PageManager, cache
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
            cache.add(self)
    
    # Hierarchy fields.

    parent = PageField(blank=True,
                       null=True)

    def get_all_parents(self):
        """Returns a list of all parents of this page."""
        if self.parent:
            return [self.parent] + self.parent.all_parents
        return []
    
    all_parents = property(get_all_parents,
                           doc="A list of all parents of this page.")

    def get_breadcrumbs(self):
        """Returns the breadcrumb trail for this page, including this page."""
        parents = self.all_parents
        parents.reverse()
        parents.append(self)
        return parents
    
    breadcrumbs = property(get_breadcrumbs,
                           doc="The breadcrumb trail for this page.")

    order = models.PositiveIntegerField(editable=False)

    def get_homepage(self):
        """Returns the homepage for this page."""
        page = self
        while page.parent:
            page = page.parent
        return page
    
    homepage = property(get_homepage,
                        doc="The homepage for this page.")

    def get_is_homepage(self):
        """Returns whether this page is the site homepage."""
        return self.parent != None
    
    is_homepage = property(get_is_homepage,
                           doc="Whether this page is the site homepage.")

    @cached_getter
    def get_children(self):
        """
        Returns all the children of this page, regardless of their publication
        state.
        """
        return Page.objects.filter(parent=self)
    
    children = property(get_children,
                        doc="All children of this page.")
    
    def get_all_children(self):
        """
        Returns all the children of this page, cascading down to their children
        too.
        """
        children = []
        for child in self.children:
            children.append(child)
            children.extend(child.all_children)
        return children
            
    all_children = property(get_all_children,
                            doc="All the children of this page, cascading down to their children too.")
    
    def get_navigation(self):
        """Returns the sub-navigation of this page."""
        return [child for child in self.children if child.in_navigation]
    
    navigation = property(get_navigation,
                          doc="The sub-navigation of this page.")
    
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
        return "/"
    
    def reverse(self, view_func, *args, **kwargs):
        """Performs a reverse URL lookup."""
        urlconf = content.lookup(self.content_type).urlconf
        return self.get_absolute_url() + urlresolvers.reverse(view_func, args=args, kwargs=kwargs, urlconf=urlconf, prefix="")
    
    def save(self, *args, **kwargs):
        """Saves the page."""
        super(Page, self).save(*args, **kwargs)
        cache.add(self)
        
    def delete(self, *args, **kwargs):
        """Deletes the page."""
        super(Page, self).delete(*args, **kwargs)
        cache.remove(self)
    
    class Meta:
        unique_together = (("parent", "url_title",),)
        ordering = ("order",)


class PageSitemap(sitemaps.PageBaseSitemap):
    
    """Sitemap for page models."""
    
    model = Page
    
    
sitemaps.registered_sitemaps["pages"] = PageSitemap