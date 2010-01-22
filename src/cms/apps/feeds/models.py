"""Models used by the feeds application."""


from django.db import models

from cms.apps.pages.models import PageBase, HtmlField


class ArticleBase(PageBase):
    
    """Base class for feed articles."""
    
    content = HtmlField(blank=True)
    
    summary = HtmlField(blank=True,
                        help_text="A short summary of this article.  If not specified, then a summarized version of the content will be used.")
    
    is_featured = models.BooleanField("featured",
                                      default=False,
                                      db_index=True,
                                      help_text="Featured articles will remain at the top of any news feeds.")
    
    