"""Admin settings for the page management application."""


from cms.core.admin import ContentAdmin, site
from cms.pages.models import Page


class PageAdmin(ContentAdmin):
    
    """Admin settings for Page models."""
    
    prepopulated_fields = {"url_title": ("title",),}
    
    fieldsets = ((None, {"fields": ("title", "url_title", "parent", "is_online",),},),
                 ("Publication", {"fields": ("publication_date", "expiry_date",),
                                  "classes": ("collapse",)}),
                 ("Navigation", {"fields": ("short_title", "in_navigation",),
                                 "classes": ("collapse",),},),) + ContentAdmin.seo_fieldsets
    
    
site.register(Page, PageAdmin)

