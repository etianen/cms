"""Content models for the site search application."""


from django.conf import settings

from cms.apps.pages import content


class SiteSearch(content.BaseContent):
    
    """A search results page."""
    
    classifier = "utilities"

    urlconf = "cms.apps.search.urls"
    
    icon = settings.CMS_MEDIA_URL + "img/content-types/site-search.png"
    
    search_engine_id = content.CharField(help_text="The Google Custom Search Engine id.")
    
    def get_fieldsets(self):
        """Returns the fieldsets used to lay out the content form."""
        return super(SiteSearch, self).get_fieldsets() + (("Search engine configuration", {"fields": ("search_engine_id",),}),)
    
    