"""Admin settings used by the news application."""


from django.contrib import admin

from cms.apps.pages.admin import site, ArticleBaseAdmin
from cms.apps.news.models import Article


class ArticleAdmin(ArticleBaseAdmin):
    
    """Admin settings used by news articles."""
    
    date_hierarchy = "publication_date"
    
    list_display = ("title", "publication_date", "is_online", "is_featured",)
    
    list_filter = ("is_online", "is_featured",)
    
    content_fieldsets = (("Article content", {"fields": ("content", "summary",),}),)
    
    publication_fieldsets = (("Publication", {"fields": ("publication_date", "is_online", "is_featured"),}),)
    
    fieldsets = ((None, {"fields": ("title", "url_title", "feed",),},),) + content_fieldsets + publication_fieldsets + ArticleBaseAdmin.navigation_fieldsets + ArticleBaseAdmin.seo_fieldsets
    
    radio_fields = {"feed": admin.VERTICAL}
    
    
site.register(Article, ArticleAdmin)

