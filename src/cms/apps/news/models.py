"""Models used by the news publication application."""


from django.db import models

from cms.apps.pages.models import Page, PageBase, PageField, HtmlField
from cms.apps.news.content import NewsFeed, NewsArticle


class Article(PageBase):
    
    """A news article."""
    
    news_feed = PageField(Page,
                          "newsfeed")
    
    content = HtmlField(blank=True,
                        null=True)
    
    summary = models.TextField(blank=True,
                               null=True,
                               help_text="A short summary of this article.  This will be used on news pages and RSS feeds.  If not specified, then a summarized version of the content will be used.")
    
    is_featured = models.BooleanField("featured",
                                      default=False,
                                      help_text="Featured articles will remain at the top of any news feeds.")
    
    def get_absolute_url(self):
        """Returns the absolute URL of the article."""
        return self.parent.content.reverse("article_detail", self.publication_date.year, self.publication_date.month, self.url_title, "")
    
    class Meta:
        verbose_name = "news article"
        unique_together = (("news_feed", "url_title",),)


Page.register_content(NewsFeed)

