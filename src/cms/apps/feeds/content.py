"""Base content class for generating feed-based applications."""


from cms.apps.pages import content


DefaultContent = content.get_default_content()


class FeedBase(DefaultContent):
    
    """Base class for feed-based content."""
    
    abstract = True
    
    classifier = "feeds"
    
    urlconf = "cms.apps.feeds.urls"
    
    article_model = None
    
    publication_date_field = "publication_date"
    
    # Article retrieval methods.
    
    def get_articles(self):
        """Returns all the associated articles."""
        return self.article_model.objects.filter(feed=self.page)
    
    def get_latest_articles(self):
        """Returns the latest articles."""
        return self.get_articles()

