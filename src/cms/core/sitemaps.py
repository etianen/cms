"""Google sitemaps used by the page managment application."""


from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sitemaps import Sitemap

from cms.core.models import PublishedBase, EntityBase, PageBase


# A dictionary of registered sitemap classes.
registered_sitemaps = {}


class PublishedBaseSitemap(Sitemap):
    
    """
    Base sitemap for all subclasses of PublishedBase.
    
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
        
    def lastmod(self, obj):
        return obj.date_modified


class EntityBaseSitemap(PublishedBaseSitemap):
    
    """
    Base sitemap for all subclasses of EntityBase.
    
    Subclasses need to override the model property.
    """
        
    def changefreq(self, obj):
        """Returns the change frequency of the given page."""
        if obj.sitemap_changefreq:
            return obj.get_sitemap_changefreq_display().lower()
        return None
        
    def priority(self, obj):
        """Returns the priority of the given page."""
        return obj.sitemap_priority
        

class PageBaseSitemap(EntityBaseSitemap):
    
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
        elif issubclass(model, EntityBase):
            sitemap_cls_base = EntityBaseSitemap
        elif issubclass(model, PublishedBase):
            sitemap_cls_base = PublishedBaseSitemap
        else:
            raise SitemapRegistrationError("You must specify a sitemap class.")
        sitemap_cls_name = model.__name__ + "Sitemap"
        sitemap_cls = type(sitemap_cls_name, (sitemap_cls_base,), {
            "model": model,
        })
    # Register the sitemap.
    registered_sitemaps[registration_key] = sitemap_cls