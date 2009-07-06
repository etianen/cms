"""Content types used by the news application."""


from django.conf import settings

from cms.apps.pages import content
from cms.apps.news.models import Article
from cms.apps.feeds import registered_feeds
from cms.apps.feeds.content import FeedBase


class NewsFeed(FeedBase):
    
    """An archive of published news articles."""
    
    article_model = Article
    
    date_field = "publication_date"
    
    icon = settings.CMS_MEDIA_URL + "img/content-types/news-feed.png"
    
    article_list_template = ("news/article_list.html", "feeds/article_list.html",)
    
    article_detail_template = ("news/article_detail.html", "feeds/article_detail.html",)
    
    article_archive_template = ("news/article_archive.html", "feeds/article_archive.html",)
    
    latest_articles_template = ("news/latest_articles.html", "feeds/latest_articles.html",)
    
    