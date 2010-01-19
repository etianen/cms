"""Google sitemaps used by the page managment application."""


from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sitemaps import Sitemap

from cms.apps.pages.models import PublishedModel


# A dictionary of registered sitemap classes.
registered_sitemaps = {}


class PageSitemap(Sitemap):
    
    """Generates a sitemap for subclasses of PublishedModel."""
    
    def items(self):
        """Returns all items in this sitemap."""
        pages = []
        for model in models.get_models():
            if issubclass(model, PublishedModel) and hasattr(model, "get_absolute_url"):
                for obj in model.objects.all():
                    # HACK: PublishedModel instances might be not be published, due to an
                    # unpublished parent. This checks to see if they can provide a URL
                    # before passing them on to the renderer.
                    try:
                        obj.get_absolute_url()
                    except ObjectDoesNotExist:
                        pass
                    else:
                        pages.append(obj)
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

