"""Content types used by the events application."""


import datetime

from django.conf import settings
from django.db.models import Q

from cms.apps.feeds.content import FeedBase


class EventsFeed(FeedBase):
    
    """An archive of published events."""
    
    icon = settings.CMS_MEDIA_URL + "img/content-types/events-feed.png"
    
    @property
    def article_model(self):
        from cms.apps.events.models import Event
        return Event
    
    def get_latest_articles(self):
        """Returns the latest events."""
        now = datetime.datetime.now()
        return self.get_articles().filter(Q(start_date__gte=now) | Q(end_date__gte=now))
    
    