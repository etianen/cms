"""Content models for the site search application."""


from django.conf import settings

from cms.apps.pages import content


DefaultContent = content.get_default_content()


class SiteSearch(DefaultContent):
    
    """A search results page."""
    
    classifier = "utilities"
    
    icon = settings.CMS_MEDIA_URL + "img/content-types/site-search.png"
    
    search_engine_id = content.CharField(help_text="The Google Custom Search Engine id.")
    
    def get_fieldsets(self):
        """Returns the fieldsets used to lay out the content form."""
        return super(SiteSearch, self).get_fieldsets() + (("Search engine configuration", {"fields": ("search_engine_id",),}),)
    
    @content.view(r"^$")
    def index(self, request):
        """Renders the search results."""
        search_term = request.GET.get("q", "")
        context = {"search_term": search_term}
        return self.render_to_response(request, "search/sitesearch.html", context)
    
    