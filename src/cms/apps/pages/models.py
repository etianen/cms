"""Core models used by the CMS."""


import datetime

from django import forms, template
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.db.models.base import ModelBase
from django.http import Http404
from django.shortcuts import render_to_response

from cms.apps.pages import content
from cms.apps.pages.forms import HtmlWidget
from cms.apps.pages.optimizations import cached_getter, cached_setter


class PageBaseManager(models.Manager):
    
    """Base managed for pages."""
    
    use_for_related_fields = True
    
    def get_query_set(self):
        """Returns the filtered query set."""
        queryset = super(PageBaseManager, self).get_query_set()
        queryset = queryset.filter(site=Site.objects.get_current())
        return queryset


class PublishedPageBaseManager(PageBaseManager):
    
    """Manager that selects only published pages."""
    
    use_for_related_fields = False
    
    def get_query_set(self):
        """Returns the filtered query set."""
        queryset = super(PublishedPageBaseManager, self).get_query_set()
        queryset = queryset.filter(is_online=True)
        return queryset


class PageBase(models.Model):
    
    """
    Base model for models used to generate a HTML page.
    
    This class is suited to pages that are to be included in feed-based views.
    For permanent or semi-permanent fixtures in a site, use the PageBase model
    instead.
    """
    
    # Model management.
    
    objects = PageBaseManager()
    
    published_objects = PublishedPageBaseManager()
    
    # Base fields.
    
    last_modified = models.DateTimeField(auto_now=True)
    
    site = models.ForeignKey(Site,
                             editable=False,
                             default=Site.objects.get_current)
    
    title = models.CharField(max_length=1000)
    
    is_online = models.BooleanField("online",
                                    default=True,
                                    help_text="Uncheck this box to remove the page from the public website.  Logged-in admin users will still be able to view this page by directly visiting it's URL.")
    
    @cached_getter
    def get_is_published(self):
        """Returns whether this page is published."""
        model = self.__class__
        try:
            model.published_objects.get(pk=self.pk)
        except model.DoesNotExist:
            return False
        return True
        
    is_published = property(get_is_published,
                            doc="Whether this page is published.")
    
    # Navigation fields.
    
    short_title = models.CharField(max_length=100,
                                   blank=True,
                                   null=True,
                                   help_text="A shorter version of the title that will be used in site navigation. Leave blank to use the full-length title.")
    
    # SEO fields.
    
    browser_title = models.CharField(max_length=1024,
                                     blank=True,
                                     null=True,
                                     help_text="The heading to use in the user's web browser.  Leave blank to use the page title.  Search engines pay particular attention to this attribute.")
    
    meta_keywords = models.CharField("keywords",
                                     max_length=1024,
                                     blank=True,
                                     null=True,
                                     help_text="A comma-separated list of keywords for this page. Use this to specify common mis-spellings or alternative versions of important words in this page.")

    meta_description = models.TextField("description",
                                        blank=True,
                                        null=True,
                                        help_text="A brief description of the contents of this page. Leave blank to use to use the parent page description.")
    
    sitemap_priority = models.FloatField("priority",
                                         choices=settings.SEO_PRIORITIES,
                                         default=settings.SEO_DEFAULT_PRIORITY,
                                         blank=True,
                                         null=True,
                                         help_text="The relative importance of this content in your site.  Search engines use this as a hint when ranking the pages within your site.")
    
    sitemap_changefreq = models.CharField("change frequency",
                                          max_length=255,
                                          choices=settings.SEO_CHANGE_FREQUENCIES,
                                          default=settings.SEO_DEFAULT_CHANGE_FREQUENCY,
                                          blank=True,
                                          null=True,
                                          help_text="How frequently you expect this content to be updated.  Search engines use this as a hint when scanning your site for updates.")
    
    robots_index = models.BooleanField("allow indexing",
                                        default=True,
                                        help_text="Uncheck this box to prevent search engines from indexing this page. Disable this only if the page contains information which you do not wish to show up in search results.")

    robots_archive = models.BooleanField("allow archiving",
                                         default=True,
                                         help_text="Uncheck this box to prevent search engines from archiving this page. Disable this only if the page is likely to change on a very regular basis.")

    robots_follow = models.BooleanField("follow links",
                                        default=True,
                                        help_text="Uncheck this box to prevent search engines from following any links they find in this page. Disable this only if the page contains links to other sites that you do not wish to publicise.")

    # Base model methods.
    
    def get_absolute_url(self):
        """All pages must publish an absolute URL."""
        raise NotImplemented
    
    url = property(lambda self: self.get_absolute_url(),
                   doc="The absolute URL of the page.")
    
    def __unicode__(self):
        """
        Returns the short title of this page, falling back to the standard
        title.
        """
        return self.short_title or self.title
    
    class Meta:
        abstract = True
        ordering = ("title",)


class PageField(models.ForeignKey):
    
    """A foreign key to a Page model."""
    
    def __init__(self, to, content_type=None, limit_choices_to=None, **kwargs):
        """Initializes the Page Field."""
        # Generate the page filter.
        if content_type is not None:
            limit_choices_to = limit_choices_to or {}
            limit_choices_to.setdefault("content_type", content_type)
        # Initialize the PageField.
        super(PageField, self).__init__(to=to, limit_choices_to=limit_choices_to, default=self.get_default, **kwargs)
        
    def get_default(self):
        """Returns the default page."""
        try:
            return self.rel.to._default_manager.filter(**self.rel.limit_choices_to)[0].pk
        except IndexError:
            return None


class HtmlField(models.TextField):
    
    """A field that contains HTML data."""
    
    def formfield(self, **kwargs):
        """Returns a HtmlWidget."""
        kwargs["widget"] = HtmlWidget
        return super(HtmlField, self).formfield(**kwargs)


class PageManager(PageBaseManager):
    
    """Manager for Page objects."""
    
    def get_homepage(self):
        """Returns the site homepage."""
        return self.get(parent=None)


class PublishedPageManager(PublishedPageBaseManager):
    
    """Manager that controls publication for dated pages."""
    
    def get_query_set(self):
        """Returns the filtered queryset."""
        now = datetime.datetime.now()
        queryset = super(PublishedPageManager, self).get_query_set()
        queryset = queryset.filter(Q(publication_date=None) | Q(publication_date__lte=now))
        queryset = queryset.filter(Q(expiry_date=None) | Q(expiry_date__gt=now))
        return queryset


class Page(PageBase):

    """A page within the site."""

    objects = PageManager()
    
    published_objects = PublishedPageManager()
    
    url_title = models.SlugField("URL title",
                                 db_index=False)
    
    # Hierarchy fields.

    parent = PageField("self",
                       blank=True,
                       null=True)

    def get_all_parents(self):
        """Returns a list of all parents of this page."""
        if self.parent:
            return [self.parent] + self.parent.all_parents
        return []
    
    all_parents = property(get_all_parents,
                           doc="A list of all parents of this page.")

    order = models.PositiveSmallIntegerField(unique=True,
                                             editable=False,
                                             blank=True,
                                             null=True)

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
    
    @cached_getter
    def get_published_children(self):
        """Returns all the published children of this page."""
        return Page.published_objects.filter(parent=self)

    published_children = property(get_published_children,
                                  doc="All the published children of this page.")

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

    @cached_getter
    def get_navigation(self):
        """
        Returns all published children that should be added to the navigation.
        """
        return self.published_children.filter(in_navigation=True)
        
    navigation = property(get_navigation,
                          doc="All published children that should be added to the navigation.")

    # Content fields.
    
    content_type = models.CharField(max_length=20,
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
        self.content_data = content.serialized_data

    content = property(get_content,
                       set_content,
                       doc="The content object associated with this page.")

    # Standard model methods.
    
    def get_absolute_url(self):
        """Generates the absolute url of the page."""
        if self.parent:
            return self.parent.url + self.url_title + "/"
        return reverse("render_homepage")
    
    class Meta:
        unique_together = (("parent", "url_title",),)
        ordering = ("order",)

