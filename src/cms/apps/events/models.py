"""Models used by the events publication application."""


import datetime

from django.db import models

from cms.apps.pages import sitemaps
from cms.apps.pages.models import PageField
from cms.apps.feeds.models import ArticleBase


class Event(ArticleBase):
    
    """A news article."""
    
    feed = PageField("eventsfeed",
                     verbose_name="events feed")
    
    start_date = models.DateField(default=lambda: datetime.datetime.now().date(),
                                  db_index=True,
                                  help_text="The date that this event is due to start.")
    
    end_date = models.DateField(blank=True,
                                null=True,
                                db_index=True,
                                help_text="The date that this event is due to end.  Leave blank for a single-day event.")
    
    date_field_name = "start_date"
    
    def get_absolute_url(self):
        """Returns the absolute URL of the article."""
        return self.feed.reverse("article_detail", self.start_date.year, self.start_date.month, self.url_title)
    
    class Meta:
        ordering = ("-is_featured", "start_date", "id")


class EventSitemap(sitemaps.PageBaseSitemap):
    
    """Sitemap for event models."""
    
    model = Event
    
    
sitemaps.registered_sitemaps["events"] = EventSitemap

