"""Content types used by the news application."""


from django.conf import settings

from cms.apps.pages import content


DefaultContent = content.get_default_content()


class NewsFeed(DefaultContent):
    
    """An archive of published news articles."""
    
    icon = settings.CMS_MEDIA_URL + "img/content-types/news-feed.png"
    
    urlconf = "cms.apps.news.urls"
    
    articles_per_page = content.PositiveIntegerField(default=10)
    
    def get_fieldsets(self):
        """Returns the fieldsets used to lay out the admin form."""
        return super(NewsFeed, self).get_fieldsets() + (("Feed details", {"fields": ("articles_per_page",),}),)
    
    