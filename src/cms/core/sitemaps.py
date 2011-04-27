"""Google sitemaps used by the page managment application."""


from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sitemaps import Sitemap


# A dictionary of registered sitemap classes.
registered_sitemaps = {}


class PageBaseSitemap(Sitemap):
    
    """
    Base sitemap for all subclasses of PageBase.
    
    Subclasses need to override the model property.
    """
    
    model = None
    
    def items(self):
        """Returns all items in this sitemap."""
        pages = []
        for obj in self.model.objects.all():
            # HACK: PublishedBase instances might be not be published, due to an
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
        if obj.sitemap_changefreq:
            return obj.get_sitemap_changefreq_display().lower()
        return None
        
    def priority(self, obj):
        """Returns the priority of the given page."""
        return obj.sitemap_priority

    def lastmod(self, obj):
        return obj.date_modified
    
