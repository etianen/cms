"""Content types used by the news application."""


from django.conf import settings

from cms.apps.feeds.content import FeedBase
from cms.apps.news.models import Article


class NewsFeed(FeedBase):
    
    """An archive of published news articles."""
    
    icon = settings.CMS_MEDIA_URL + "img/content-types/news-feed.png"
    
    article_model = Article
    
    