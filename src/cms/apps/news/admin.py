"""Admin settings used by the news application."""


from django.contrib import admin

from cms.apps.pages.admin import site, ArticleBaseAdmin
from cms.apps.news.models import Article


class ArticleAdmin(ArticleBaseAdmin):
    
    """Admin settings used by news articles."""
    
    list_display = ("title", "publication_date", "is_online", "is_featured",)
    
    list_filter = ("is_online", "is_featured",)
    
    content_fieldsets = (("Article content", {"fields": ("content", "summary",),}),)
    
    publication_fieldsets = (("Publication", {"fields": ("publication_date", "is_online", "is_featured"),
                                              "classes": ("collapse",)}),)
    
    fieldsets = ((None, {"fields": ("title", "url_title", "news_feed",),},),) + content_fieldsets + publication_fieldsets + ArticleBaseAdmin.navigation_fieldsets + ArticleBaseAdmin.seo_fieldsets
    
    radio_fields = {"news_feed": admin.VERTICAL}
    
    
site.register(Article, ArticleAdmin)

