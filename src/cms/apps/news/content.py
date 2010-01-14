"""Content types used by the news application."""


from django.conf import settings

from cms.apps.news.models import Article
from cms.apps.feeds.content import FeedBase


class NewsFeed(FeedBase):
    
    """An archive of published news articles."""
    
    article_model = Article
    
    date_field = "publication_date"
    
    icon = settings.CMS_MEDIA_URL + "img/content-types/news-feed.png"
    
    article_list_template = "news/article_list.html"
    
    year_archive_template = "feeds/year_archive.html"
    
    month_archive_template = "feeds/month_archive.html"
    
    article_detail_template = "news/article_detail.html"
    
    article_archive_template = "news/article_archive.html"
    
    latest_articles_template = "news/latest_articles.html"
    
    