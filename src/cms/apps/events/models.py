"""Models used by the events publication application."""


import datetime

from django.db import models

from cms.apps.pages.models import PageField, PageBase, HtmlField


class Event(PageBase):
    
    """A news article."""
    
    feed = PageField("eventsfeed",
                     verbose_name="events feed")
    
    content = HtmlField(blank=True)
    
    summary = HtmlField(blank=True,
                        help_text="A short summary of this article.  If not specified, then a summarized version of the content will be used.")
    
    is_featured = models.BooleanField("featured",
                                      default=False,
                                      db_index=True,
                                      help_text="Featured events will remain at the top of any events feeds.")
    
    # Publication fields.
    
    start_date = models.DateField(default=lambda: datetime.datetime.now().date(),
                                  db_index=True,
                                  help_text="The date that this event is due to start.")
    
    end_date = models.DateField(blank=True,
                                null=True,
                                db_index=True,
                                help_text="The date that this event is due to end.  Leave blank for a single-day event.")
    
    def get_absolute_url(self):
        """Returns the absolute URL of the article."""
        return self.feed.content.reverse("object_detail", self.start_date.year, self.start_date.month, self.url_title)
    
    class Meta:
        unique_together = (("feed", "url_title",),)
        ordering = ("-is_featured", "start_date", "id")

