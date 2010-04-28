"""Admin settings used by the news application."""


from django.contrib import admin

from cms.apps.pages.admin import site, PageBaseAdmin
from cms.apps.events.models import Event


class EventAdmin(PageBaseAdmin):
    
    """Admin settings used by news articles."""
    
    date_hierarchy = "start_date"
    
    list_display = ("title", "start_date", "is_online", "is_featured", "get_date_modified",)
    
    list_filter = ("is_online", "is_featured",)
    
    content_fieldsets = (("Event content", {"fields": ("content", "summary",),}),)
    
    publication_fieldsets = (("Publication", {"fields": ("start_date", "end_date", "is_online", "is_featured"),}),)
    
    fieldsets = ((None, {"fields": ("title", "url_title", "feed",),},),) + content_fieldsets + publication_fieldsets + PageBaseAdmin.navigation_fieldsets + PageBaseAdmin.seo_fieldsets
    
    radio_fields = {"feed": admin.VERTICAL}
    
    
site.register(Event, EventAdmin)

