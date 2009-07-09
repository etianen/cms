"""Abstract base models used by the page management application."""


import datetime

from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import Q

from cms.apps.pages.models.managers import PublishedModelManager, PageBaseManager


class PublishedModel(models.Model):
    
    """A model with publication controls."""
    
    objects = PublishedModelManager()
    
    @classmethod
    def select_published(cls, queryset):
        """
        Filters out unpublished objects from the given queryset.
        
        This method will automatically be applied to all querysets of this model
        when in an active publication context.
        
        Subclasses can override this method to define additinal publication
        rules.
        """
        return queryset.filter(is_online=True)
    
    is_online = models.BooleanField("online",
                                    default=True,
                                    help_text="Uncheck this box to remove the page from the public website.  Logged-in admin users will still be able to view this page by directly visiting it's URL.")
    
    # Nicer alias for URL generation.
    
    def get_absolute_url(self):
        """All pages must publish an absolute URL."""
        raise NotImplemented
    
    url = property(lambda self: self.get_absolute_url(),
                   doc="The absolute URL of the page.")
    
    class Meta:
        abstract = True
    

# Choices available to the meta robots clauses.
ROBOTS_CHOICES = ((1, "Yes"),
                  (0, "No"),)


class PageBase(PublishedModel):
    
    """
    Base model for models used to generate a HTML page.
    
    This class is suited to pages that are to be included in feed-based views.
    For permanent or semi-permanent fixtures in a site, use the PageBase model
    instead.
    """
    
    objects = PageBaseManager()
    
    # Base fields.
    
    last_modified = models.DateTimeField(auto_now=True)
    
    site = models.ForeignKey(Site,
                             editable=False,
                             default=Site.objects.get_current)
    
    title = models.CharField(max_length=1000)
    
    # Navigation fields.
    
    short_title = models.CharField(max_length=200,
                                   blank=True,
                                   help_text="A shorter version of the title that will be used in site navigation. Leave blank to use the full-length title.")
    
    # SEO fields.
    
    browser_title = models.CharField(max_length=1000,
                                     blank=True,
                                     help_text="The heading to use in the user's web browser.  Leave blank to use the page title.  Search engines pay particular attention to this attribute.")
    
    meta_keywords = models.CharField("keywords",
                                     max_length=1000,
                                     blank=True,
                                     help_text="A comma-separated list of keywords for this page. Use this to specify common mis-spellings or alternative versions of important words in this page.")

    meta_description = models.TextField("description",
                                        blank=True,
                                        help_text="A brief description of the contents of this page. Leave blank to use to use the parent page description.")
    
    sitemap_priority = models.FloatField("priority",
                                         choices=settings.SEO_PRIORITIES,
                                         default=settings.SEO_DEFAULT_PRIORITY,
                                         blank=True,
                                         null=True,
                                         help_text="The relative importance of this content in your site.  Search engines use this as a hint when ranking the pages within your site.")
    
    sitemap_changefreq = models.CharField("change frequency",
                                          max_length=7 ,
                                          choices=settings.SEO_CHANGE_FREQUENCIES,
                                          default=settings.SEO_DEFAULT_CHANGE_FREQUENCY,
                                          blank=True,
                                          null=True,
                                          help_text="How frequently you expect this content to be updated.  Search engines use this as a hint when scanning your site for updates.")
    
    robots_index = models.PositiveSmallIntegerField("allow indexing",
                                                    blank=True,
                                                    null=True,
                                                    default=None,
                                                    choices=ROBOTS_CHOICES,
                                                    help_text="Use this to prevent search engines from indexing this page. Disable this only if the page contains information which you do not wish to show up in search results. Leave blank to use the setting from the parent page.")

    robots_archive = models.PositiveSmallIntegerField("allow archiving",
                                                      blank=True,
                                                      null=True,
                                                      default=None,
                                                      choices=ROBOTS_CHOICES,
                                                      help_text="Use this to prevent search engines from archiving this page. Disable this only if the page is likely to change on a very regular basis. Leave blank to use the setting from the parent page.")

    robots_follow = models.PositiveSmallIntegerField("follow links",
                                                     blank=True,
                                                     null=True,
                                                     default=None,
                                                     choices=ROBOTS_CHOICES,
                                                     help_text="Use this to prevent search engines from following any links they find in this page. Disable this only if the page contains links to other sites that you do not wish to publicise. Leave blank to use the setting from the parent page.")
    
    # Base model methods.
    
    def __unicode__(self):
        """
        Returns the short title of this page, falling back to the standard
        title.
        """
        return self.short_title or self.title
    
    class Meta:
        abstract = True
        ordering = ("title",)

