"""Models used by the news publication application."""


from django.db import models

from cms.apps.pages.models import Page, PageBase, PageField
from cms.apps.news.content import NewsFeed, NewsArticle


class Article(PageBase):
    
    """A news article."""
    
    parent = PageField(Page,
                       "newsfeed",
                       verbose_name="news page")
    
    class Meta:
        verbose_name = "news article"
        
        
Article.register_content(NewsArticle, "content")


Page.register_content(NewsFeed)

