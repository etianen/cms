"""Content types used by the events application."""


import datetime

from django.conf import settings

from cms.apps.pages import content
from cms.apps.feeds.content import FeedBase
from cms.apps.events.models import Event


class EventsFeed(FeedBase):
    
    """An archive of published news articles."""
    
    article_model = Event
    
    date_field = "start_date"
    
    icon = settings.CMS_MEDIA_URL + "img/content-types/events-feed.png"
    
    article_list_template = ("events/article_list.html", "feeds/article_list.html",)
    
    article_detail_template = ("events/article_detail.html", "feeds/article_detail.html",)
    
    article_archive_template = ("events/article_archive.html", "feeds/article_archive.html",)
    
    latest_articles_template = ("events/latest_articles.html", "feeds/latest_articles.html",)
    
    def get_latest_articles(self):
        """Returns the list of articles for the latest article feeds."""
        return super(EventsFeed, self).get_latest_articles().filter(start_date__gte=datetime.datetime.now().date())
    
    
content.register(EventsFeed)

