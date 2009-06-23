"""Admin settings used by the news application."""


from django.contrib import admin

from cms.apps.pages.admin import site, PageBaseAdmin
from cms.apps.news.models import Article


class ArticleAdmin(PageBaseAdmin):
    
    """Admin settings used by news articles."""
    
    fieldsets = ((None, {"fields": ("title", "url_title", "parent",),},),) + PageBaseAdmin.navigation_fieldsets + PageBaseAdmin.publication_fieldsets + PageBaseAdmin.seo_fieldsets
    
    radio_fields = {"parent": admin.VERTICAL}
    
    
site.register(Article, ArticleAdmin)

