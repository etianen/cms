"""Models used by the news publication application."""


import datetime

from django.db import models

from cms.apps.pages.models import Page, PageField, HtmlField, PublishedPageBaseManager, PageBaseManager
from cms.apps.feeds.models import ArticleBase


class PublishedArticleManager(PublishedPageBaseManager):
    
    """Manager that controls publication for news articles."""
    
    def get_query_set(self):
        """Returns the filtered queryset."""
        now = datetime.datetime.now()
        queryset = super(PublishedArticleManager, self).get_query_set()
        queryset = queryset.filter(publication_date__lte=now)
        return queryset


class Article(ArticleBase):
    
    """A news article."""
    
    objects = PageBaseManager()
    
    published_objects = PublishedArticleManager()
    
    feed = PageField("newsfeed",
                     verbose_name="news feed")
    
    publication_date = models.DateField(default=lambda: datetime.datetime.now().date(),
                                        db_index=True,
                                        help_text="The date that this article will appear on the website.")
    
    def get_absolute_url(self):
        """Returns the absolute URL of the article."""
        return self.feed.content.reverse("article_detail", self.publication_date.year, self.publication_date.month, self.url_title)
    
    class Meta:
        verbose_name = "news article"
        ordering = ("-is_featured", "-publication_date", "-id")

