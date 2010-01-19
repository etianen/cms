"""Some base classes for articles."""


from django.db import models

from cms.apps.pages.models import PageBase, HtmlField


class ArticleBase(PageBase):
    
    """
    Base class for feed articles.
    
    Subclasses must provide a 'feed' property, a 'get_absolute_url' method and
    a default ordering clause.  They should also include an indexed date field
    used to order the articles.
    
    Subclasses must also place a unique_together constraint on the 'feed' and
    'url_title' columns.
    """
    
    content = HtmlField(blank=True)
    
    summary = HtmlField(blank=True,
                        help_text="A short summary of this article.  If not specified, then a summarized version of the content will be used.")
    
    is_featured = models.BooleanField("featured",
                                      default=False,
                                      db_index=True,
                                      help_text="Featured articles will remain at the top of any news feeds.")
    
    class Meta:
        abstract = True
        
        