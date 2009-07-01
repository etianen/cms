"""Models used by the news publication application."""


import datetime

from django.db import models

from cms.apps.pages.models import Page, ArticleBase, PageField, HtmlField


class Event(ArticleBase):
    
    """A news article."""
    
    events_feed = PageField(Page,
                           "eventsfeed")
    
    content = HtmlField(blank=True,
                        null=True)
    
    summary = HtmlField(blank=True,
                        null=True,
                        help_text="A short summary of this event.  This will be used on events pages and RSS feeds.  If not specified, then a summarized version of the content will be used.")
    
    # Publication fields.
    
    start_date = models.DateField(default=lambda: datetime.datetime.now().date(),
                                  help_text="The date that this event is due to start.")
    
    end_date = models.DateField(blank=True,
                                null=True,
                                help_text="The date that this event is due to end.  Leave blank for a single-day event.")
    
    is_featured = models.BooleanField("featured",
                                      default=False,
                                      help_text="Featured events will remain at the top of any news feeds.")
    
    def get_absolute_url(self):
        """Returns the absolute URL of the article."""
        return self.events_feed.content.reverse("event_detail", self.start_date.year, self.start_date.month, self.url_title)
    
    class Meta:
        unique_together = (("events_feed", "url_title",),)
        ordering = ("-is_featured", "start_date", "id")

