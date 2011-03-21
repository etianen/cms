"""Abstract base models used by the page management application."""

from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.shortcuts import render

from cms.core.models.managers import PublishedModelManager, PageBaseManager
from cms.core.models.fields import NullBooleanField, EnumField


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
    
    date_created = models.DateTimeField(auto_now_add=True)
    
    date_modified = models.DateTimeField("last modified",
                                         auto_now=True)
    
    is_online = models.BooleanField("online",
                                    default=True,
                                    help_text="Uncheck this box to remove the page from the public website.  Logged-in admin users will still be able to view this page by clicking the 'view on site' button.")
    
    # Default class properties for sitemap generation.
    
    sitemap_changefreq = None
    
    sitemap_priority = None
    
    class Meta:
        abstract = True
    

class PageBase(PublishedModel):
    
    """
    Base model for models used to generate a HTML page.
    
    This class is suited to pages that are to be included in feed-based views.
    For permanent or semi-permanent fixtures in a site, use the PageBase model
    instead.
    """
    
    objects = PageBaseManager()
    
    # Base fields.
    
    site = models.ForeignKey(Site,
                             editable=False,
                             default=Site.objects.get_current)
    
    url_title = models.SlugField("URL title",
                                 db_index=False)
    
    title = models.CharField(
        max_length = 1000,
        db_index = True
    )
    
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
                                        help_text="A brief description of the contents of this page.")
    
    sitemap_priority = models.FloatField("priority",
                                         choices=settings.SEO_PRIORITIES,
                                         default=None,
                                         blank=True,
                                         null=True,
                                         help_text="The relative importance of this content in your site.  Search engines use this as a hint when ranking the pages within your site.")

    sitemap_changefreq = EnumField("change frequency",
                                   choices=((1, "always", "Always"),
                                            (2, "hourly", "Hourly"),
                                            (3, "daily", "Daily"),
                                            (4, "weekly", "Weekly"),
                                            (5, "monthly", "Monthly"),
                                            (6, "yearly", "Yearly"),
                                            (7, "never", "Never")),
                                   default=None,
                                   blank=True,
                                   null=True,
                                   help_text="How frequently you expect this content to be updated.  Search engines use this as a hint when scanning your site for updates.")
    
    robots_index = NullBooleanField("allow indexing",
                                    blank=True,
                                    default=None,
                                    help_text="Use this to prevent search engines from indexing this page. Disable this only if the page contains information which you do not wish to show up in search results. Leave blank to use the setting from the parent page.")

    robots_follow = NullBooleanField("follow links",
                                     blank=True,
                                     default=None,
                                     help_text="Use this to prevent search engines from following any links they find in this page. Disable this only if the page contains links to other sites that you do not wish to publicise. Leave blank to use the setting from the parent page.")

    robots_archive = NullBooleanField("allow archiving",
                                      blank=True,
                                      default=None,
                                      help_text="Use this to prevent search engines from archiving this page. Disable this only if the page is likely to change on a very regular basis. Leave blank to use the setting from the parent page.")
    
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

