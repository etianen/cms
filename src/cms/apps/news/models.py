"""Models used by the news publication application."""


import datetime

from django.db import models

from cms.apps.pages.models import Page, PageField, HtmlField, PageBaseManager
from cms.apps.feeds.models import ArticleBase


class Article(ArticleBase):
    
    """A news article."""
    
    @classmethod
    def select_published(cls, queryset):
        """Filters out unpublished articles."""
        queryset = super(Article, cls).select_published(queryset)
        now = datetime.datetime.now()
        queryset = queryset.filter(publication_date__lte=now)
        return queryset
    
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

