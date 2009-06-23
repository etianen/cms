"""Content types used by the news application."""


from django.conf import settings

from cms.apps.pages import content


class NewsFeed(content.Content):
    
    """An archive of published news articles."""
    
    icon = settings.CMS_MEDIA_URL + "img/content-types/news-feed.png"
    
    articles_per_page = content.PositiveIntegerField(required=True,
                                                     default=10)
    

class NewsArticle(content.Content):
    
    """A published news article."""
    
    summary = content.TextField(help_text="A short summary of this article.  This will be used on news pages and RSS feeds.  If not specified, then a summarized version of the content will be used.")
    
    