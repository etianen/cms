"""Models used by the news publication application."""


import datetime

from django.db import models

from cms.core import sitemaps
from cms.apps.pages.models import PageField
from cms.apps.feeds.models import ArticleBase
from cms.apps.news.content import NewsFeed


class Article(ArticleBase):
    
    """A news article."""
    
    @classmethod
    def select_published(cls, queryset):
        """Filters out unpublished articles."""
        queryset = super(Article, cls).select_published(queryset)
        now = datetime.datetime.now()
        queryset = queryset.filter(publication_date__lte=now)
        return queryset
    
    feed = PageField(NewsFeed,
                     verbose_name="news feed")
    
    publication_date = models.DateField(default=lambda: datetime.datetime.now().date(),
                                        db_index=True,
                                        help_text="The date that this article will appear on the website.")
    
    class Meta:
        verbose_name = "news article"
        ordering = ("-is_featured", "-publication_date", "-id")


class ArticleSitemap(sitemaps.PageBaseSitemap):
    
    """Sitemap for article models."""
    
    model = Article
    
    
sitemaps.registered_sitemaps["articles"] = ArticleSitemap

