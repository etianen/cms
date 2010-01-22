"""Base content class for generating feed-based applications."""


from cms.apps.pages import content


DefaultContent = content.get_default_content()


class FeedBase(DefaultContent):
    
    """Base class for feed-based content."""
    
    abstract = True
    
    classifier = "feeds"
    
    urlconf = "cms.apps.feeds.urls"
    
    articles_per_page = content.PositiveIntegerField(default=10)
    
    article_model = None
    
    publication_date_field = "publication_date"
    
    def get_fieldsets(self):
        """Returns the fieldsets used to lay out the admin form."""
        return super(FeedBase, self).get_fieldsets() + (("Feed details", {"fields": ("events_per_page",),}),)
    
    # Article retrieval methods.
    
    def get_articles(self):
        """Returns all the associated articles."""
        return self.article_model.objects.filter(feed=self.page)
    
    def get_latest_articles(self):
        """Returns the latest articles."""
        return self.get_articles()

