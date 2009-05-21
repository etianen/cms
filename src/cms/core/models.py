"""Core models used by the CMS."""


from django import forms
from django.conf import settings
from django.db import models

from cms.core.widgets import HtmlWidget


class PublishedManager(models.Manager):
    
    """Manager that only returns published content."""
    
    def get_query_set(self):
        """Returns all content that is published."""
        queryset = super(PublishedManager, self).get_query_set()
        queryset = queryset.filter(is_online=True)
        return queryset


class ContentModel(models.Model):
    
    """Base model for all website content."""
    
    objects = models.Manager()
    
    published_objects = PublishedManager()
    
    # Base fields.
    
    title = models.CharField(max_length=1000)
    
    last_modified = models.DateTimeField(auto_now=True,
                                         help_text="The date and time of when this content was last modified.")
    
    # Publication fields.
    
    is_online = models.BooleanField("online",
                                    default=True)
    
    # SEO fields.
    
    browser_title = models.CharField(max_length=1024,
                                     blank=True,
                                     null=True,
                                     help_text="The heading to use in the user's web browser.  Leave blank to use the page title.  Search engines page particular attention to this attribute.")
    
    keywords = models.CharField(max_length=1024,
                                blank=True,
                                null=True,
                                help_text="A comma-separated list of keywords for this page. Use this to specify common mis-spellings or alternative versions of important words in this page.")

    description = models.TextField(blank=True,
                                   null=True,
                                   help_text="A brief description of the contents of this page. Leave blank to use to use the parent page description.")
    
    priority = models.FloatField(choices=settings.SEO_PRIORITIES,
                                 default=settings.SEO_DEFAULT_PRIORITY,
                                 blank=True,
                                 null=True,
                                 help_text="The relative importance of this content in your site.  Search engines use this as a hint when ranking the pages within your site.")
    
    change_frequency = models.CharField(max_length=255,
                                        choices=settings.SEO_CHANGE_FREQUENCIES,
                                        default=settings.SEO_DEFAULT_CHANGE_FREQUENCY,
                                        blank=True,
                                        null=True,
                                        help_text="How frequently you expect this content to be updated.  Search engines use this as a hint when scanning your site for updates.")
    
    allow_indexing = models.BooleanField(default=True,
                                         help_text="Uncheck this box to prevent search engines from indexing this page. Disable this only if the page contains information which you do not wish to show up in search results.")

    allow_archiving = models.BooleanField(default=True,
                                          help_text="Uncheck this box to prevent search engines from archiving this page. Disable this only if the page is likely to change on a very regular basis.")

    follow_links = models.BooleanField(default=True,
                                       help_text="Uncheck this box to prevent search engines from following any links they find in this page. Disable this only if the page contains links to other sites that you do not wish to publicise.")
    
    # Base model methods.
    
    def __unicode__(self):
        """Returns the title of the content."""
        return self.title
    
    class Meta:
        abstract = True
        ordering = ("title",)
        verbose_name_plural = "content"
        
