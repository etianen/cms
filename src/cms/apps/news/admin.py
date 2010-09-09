"""Admin settings used by the news application."""


from django.contrib import admin

from cms.core.admin import site, PageBaseAdmin
from cms.apps.news.models import Article


class ArticleAdmin(PageBaseAdmin):
    
    """Admin settings used by news articles."""
    
    date_hierarchy = "publication_date"
    
    list_display = ("title", "publication_date", "is_online", "is_featured", "get_date_modified",)
    
    list_filter = ("is_online", "is_featured",)
    
    content_fieldsets = (("Article content", {"fields": ("content", "summary",),}),)
    
    publication_fieldsets = (("Publication", {"fields": ("publication_date", "is_online", "is_featured",),}),)
    
    fieldsets = ((None, {"fields": ("title", "url_title", "feed",),},),) + content_fieldsets + publication_fieldsets + PageBaseAdmin.navigation_fieldsets + PageBaseAdmin.seo_fieldsets
    
    radio_fields = {"feed": admin.VERTICAL}
    
    
site.register(Article, ArticleAdmin)

