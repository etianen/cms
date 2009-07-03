"""Google sitemaps used by the page managment application."""


from itertools import chain

from django.db import models
from django.conf import settings
from django.contrib.sitemaps import Sitemap

from cms.apps.pages.models import PageBase
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


# A dictionary of registered sitemap classes.
registered_sitemaps = {}


class PageSitemap(BaseSitemap):
    
    """Generates a sitemap for subclasses of PageBase."""
    
    def items(self):
        """Returns all items in this sitemap."""
        pages = []
        for model in models.get_models():
            if issubclass(model, PageBase):
                pages.append(model.published_objects.all().iterator())
        return chain(*pages)
        
    def changefreq(self, obj):
        """Returns the change frequency of the given page."""
        return obj.sitemap_changefreq
        
    def priority(self, obj):
        """Returns the priority of the given page."""
        return obj.sitemap_priority

    def lastmod(self, obj):
        return obj.last_modified
    
    
registered_sitemaps["pages"] = PageSitemap

