"""Content types used by the events application."""


from django.conf import settings

from cms.apps.pages import content


DefaultContent = content.get_default_content()


class EventsFeed(DefaultContent):
    
    """An archive of published events."""
    
    icon = settings.CMS_MEDIA_URL + "img/content-types/events-feed.png"
    
    urlconf = "cms.apps.events.urls"
    
    events_per_page = content.PositiveIntegerField(default=10)
    
    def get_fieldsets(self):
        """Returns the fieldsets used to lay out the admin form."""
        return super(EventsFeed, self).get_fieldsets() + (("Feed details", {"fields": ("events_per_page",),}),)
    
    