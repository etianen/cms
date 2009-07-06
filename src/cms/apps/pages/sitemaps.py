"""Google sitemaps used by the page managment application."""


from itertools import chain

from django.db import models
from django.conf import settings
from django.contrib.sitemaps import Sitemap

from cms.apps.pages.models import PageBase


# A dictionary of registered sitemap classes.
registered_sitemaps = {}


class PageSitemap(Sitemap):
    
    """Generates a sitemap for subclasses of PageBase."""
    
    def items(self):
        """Returns all items in this sitemap."""
        pages = []
        for model in models.get_models():
            if issubclass(model, PageBase):
                pages.extend(model.objects.all())
        return pages
        
    def changefreq(self, obj):
        """Returns the change frequency of the given page."""
        return obj.sitemap_changefreq
        
    def priority(self, obj):
        """Returns the priority of the given page."""
        return obj.sitemap_priority

    def lastmod(self, obj):
        return obj.last_modified
    
    
registered_sitemaps["pages"] = PageSitemap

