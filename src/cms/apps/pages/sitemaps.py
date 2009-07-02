"""Google sitemaps used by the page managment application."""


from django.db import models
from django.conf import settings
from django.contrib.sitemaps import Sitemap

from cms.apps.pages.models import ArticleBase
from cms.apps.pages.sites import add_domain


class BaseSitemap(Sitemap):
    
    """A sitemap implementation that does not requires the sites framework."""
    
    def get_urls(self, page=1):
        """Returns the list of URLS."""
        urls = []
        
        for item in self.paginator.page(page).object_list:
            url_info = {"location": add_domain(self._Sitemap__get("location", item)),
                        "lastmod": self._Sitemap__get("lastmod", item, None),
                        "changefreq": self._Sitemap__get("changefreq", item, None),
                        "priority": self._Sitemap__get("priority", item, None)}
            urls.append(url_info)
        return urls


class PageSitemap(BaseSitemap):
    
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
        
        