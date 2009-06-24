"""Models used by the news publication application."""


from django.db import models

from cms.apps.pages.models import Page, PageBase, PageField
from cms.apps.news.content import NewsFeed, NewsArticle


class Article(PageBase):
    
    """A news article."""
    
    parent = PageField(Page,
                       "newsfeed",
                       verbose_name="news feed")
    
    is_featured = models.BooleanField("featured",
                                      default=False,
                                      help_text="Featured articles will remain at the top of any news feeds.")
    
    def get_absolute_url(self):
        """Returns the absolute URL of the article."""
        try:
            return self.parent.content.reverse("article_detail", self.publication_date.year, self.publication_date.month, self.url_title)
        except Exception, ex:
            print ex
    
    class Meta:
        verbose_name = "news article"
        
        
Article.register_content(NewsArticle, "content")


Page.register_content(NewsFeed)

