"""Base classes for the CMS admin interface."""

from django.contrib import admin

from cms import externals
from cms.models.base import SearchMetaBaseSearchAdapter, PageBaseSearchAdapter
            

class PublishedBaseAdmin(admin.ModelAdmin):
    
    """Base admin class for published models."""
    
    change_form_template = "admin/cms/publishedmodel/change_form.html"


class OnlineBaseAdmin(PublishedBaseAdmin):
    
    """Base admin class for OnlineModelBase instances."""
    
    actions = ("publish_selected", "unpublish_selected",)
    
    list_display = ("__unicode__", "is_online",)
    
    list_filter = ("is_online",)
    
    PUBLICATION_FIELDS = ("Publication", {
        "fields": ("is_online",),
        "classes": ("collapse",),
    })
    
    # Custom admin actions.
    
    def publish_selected(self, request, queryset):
        """Publishes the selected models."""
        queryset.update(is_online=True)
    publish_selected.short_description = "Place selected %(verbose_name_plural)s online"
    
    def unpublish_selected(self, request, queryset):
        """Unpublishes the selected models."""
        queryset.update(is_online=False)
    unpublish_selected.short_description = "Take selected %(verbose_name_plural)s offline"
    

class SearchMetaBaseAdmin(OnlineBaseAdmin):
    
    """Base admin class for SearchMetaBase models."""
    
    adapter_cls = SearchMetaBaseSearchAdapter
    
    list_display = ("__unicode__", "is_online",)
    
    SEO_FIELDS = ("Search engine optimization", {
        "fields": ("browser_title", "meta_keywords", "meta_description", "sitemap_priority", "sitemap_changefreq", "robots_index", "robots_follow", "robots_archive",),
        "classes": ("collapse",),
    })
    
    
if externals.reversion:
    class SearchMetaBaseAdmin(SearchMetaBaseAdmin, externals.reversion["admin.VersionMetaAdmin"]):
        list_display = SearchMetaBaseAdmin.list_display + ("get_date_modified",)
    
    
if externals.watson:
    class SearchMetaBaseAdmin(SearchMetaBaseAdmin, externals.watson["admin.SearchAdmin"]):
        pass


class PageBaseAdmin(SearchMetaBaseAdmin):
    
    """Base admin class for PageBase models."""
    
    prepopulated_fields = {"url_title": ("title",),}
    
    search_fields = ("title", "short_title", "meta_keywords", "meta_description",)
    
    adapter_cls = PageBaseSearchAdapter
    
    TITLE_FIELDS = (None, {
        "fields": ("title", "url_title",),
    })
    
    NAVIGATION_FIELDS = ("Navigation", {
        "fields": ("short_title",),
        "classes": ("collapse",),
    })
    
    fieldsets = (
        TITLE_FIELDS,
        OnlineBaseAdmin.PUBLICATION_FIELDS,
        NAVIGATION_FIELDS,
        SearchMetaBaseAdmin.SEO_FIELDS,
    )