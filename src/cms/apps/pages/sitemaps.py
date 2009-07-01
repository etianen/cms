"""Google sitemaps used by the page managment application."""


from django.db import models
from django.contrib.sitemaps import Sitemap

from cms.apps.pages.models import ArticleBase


class PageSitemap(Sitemap):
    
    """Generates a sitemap for subclasses of PageBase."""
    
    def __init__(self, page_cls):
        """Initializes the PageSitemap."""
        self.page_cls = page_cls
        
    def items(self):
        """Returns all items in this sitemap."""
        return self.page_cls.published_objects.all()
        
    def changefreq(self, obj):
        """Returns the change frequency of the given page."""
        return obj.sitemap_changefreq
        
    def priority(self, obj):
        """Returns the priority of the given page."""
        return obj.sitemap_priority

    def lastmod(self, obj):
        return obj.last_modified
    
    
# A dictionary of registered sitemap classes.
registered_sitemaps = {}


# Register all know page types.
for model in models.get_models():
    if issubclass(model, ArticleBase):
        sitemap_key = "%s-%s" % (model._meta.app_label, model.__name__.lower())
        registered_sitemaps[sitemap_key] = PageSitemap(model)
        
        