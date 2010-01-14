"""Content types used by the events application."""


import datetime

from django.conf import settings
from django.db.models import Q

from cms.apps.feeds.content import FeedBase
from cms.apps.events.models import Event


class EventsFeed(FeedBase):
    
    """An archive of published news articles."""
    
    article_model = Event
    
    date_field = "start_date"
    
    icon = settings.CMS_MEDIA_URL + "img/content-types/events-feed.png"
    
    article_list_template = "events/article_list.html"
    
    year_archive_template = "events/year_archive.html"
    
    month_archive_template = "events/month_archive.html"
    
    article_detail_template = "events/article_detail.html"
    
    article_archive_template = "events/article_archive.html"
    
    latest_articles_template = "events/latest_articles.html"
    
    def get_latest_articles(self):
        """Returns the list of articles for the latest article feeds."""
        events = super(EventsFeed, self).get_latest_articles()
        now = datetime.datetime.now().date()
        events = events.filter(Q(start_date__gte=now) | Q(end_date__gte=now))
        return events
    
    