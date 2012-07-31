"""Google sitemaps used by the page managment application."""

from django.contrib.sitemaps import Sitemap

from cms.models import PublishedBase, OnlineBase, SearchMetaBase, PageBase


# A dictionary of registered sitemap classes.
registered_sitemaps = {}


class BaseSitemap(Sitemap):
    
    """
    Base sitemap for registration.
    
    Subclasses need to override the model property.
    """
    
    model = None
    
    def items(self):
        """Returns all items in this sitemap."""
        return self.model.objects.all()
    
    
class PublishedBaseSitemap(BaseSitemap):
    
    """Base sitemap for all subclasses of PublishedBase."""
    
    
class OnlineBaseSitemap(PublishedBaseSitemap):
    
    """Base sitemap for all subclasses of OnlineBase."""


class SearchMetaBaseSitemap(OnlineBaseSitemap):
    
    """Base sitemap for all subclasses of SearchMetaBase."""
    
    def items(self):
        """Only lists items that are marked as indexable."""
        return super(SearchMetaBaseSitemap, self).items().filter(
            robots_index = True,
        )
     
    def changefreq(self, obj):
        """Returns the change frequency of the given page."""
        if obj.sitemap_changefreq:
            return obj.get_sitemap_changefreq_display().lower()
        return None
        
    def priority(self, obj):
        """Returns the priority of the given page."""
        return obj.sitemap_priority
        

class PageBaseSitemap(SearchMetaBaseSitemap):
    
    """
    Base sitemap for all subclasses of PageBase.
    
    Subclasses need to override the model property.
    """


class SitemapRegistrationError(Exception):

    """Error raised when a sitemap could not be registered."""
    
    
def register(model, sitemap_cls=None):
    """Registers a model with the sitemap registry."""
    # Generate the registration key.
    registration_key = u"{app_label}-{model_name}".format(
        app_label = model._meta.app_label,
        model_name = model.__name__.lower(),
    )
    if registration_key in registered_sitemaps:
        raise SitemapRegistrationError(u"A sitemap has already been registered under {registration_key}".format(
            registration_key = registration_key,
        ))
    # Generate the sitemap class.
    if not sitemap_cls:
        if issubclass(model, PageBase):
            sitemap_cls_base = PageBaseSitemap
        elif issubclass(model, SearchMetaBase):
            sitemap_cls_base = SearchMetaBaseSitemap
        elif issubclass(model, OnlineBase):
            sitemap_cls_base = OnlineBaseSitemap
        elif issubclass(model, PublishedBase):
            sitemap_cls_base = PublishedBaseSitemap
        else:
            sitemap_cls_base = BaseSitemap
        sitemap_cls_name = model.__name__ + "Sitemap"
        sitemap_cls = type(sitemap_cls_name, (sitemap_cls_base,), {
            "model": model,
        })
    # Register the sitemap.
    registered_sitemaps[registration_key] = sitemap_cls