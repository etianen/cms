"""Content types used by the news application."""


from django.conf import settings

from cms.apps.feeds.content import FeedBase


class NewsFeed(FeedBase):
    
    """An archive of published news articles."""
    
    icon = settings.CMS_MEDIA_URL + "img/content-types/news-feed.png"
    
    @property
    def article_model(self):
        from cms.apps.news.models import Article
        return Article