"""
Page management application.

This forms the core of the CMS functionality.
"""


from django.contrib.sites.models import SITE_CACHE
from django.conf import settings

from cms.apps.pages import content


content.autoregister()


# HACK: Give the sites framework a default site.


class CurrentSite(object):
    
    """A site object created from the settings file."""
    
    def __init__(self):
        """Initializes the CurrentSite."""
        self.name = settings.SITE_NAME
        self.domain = settings.SITE_DOMAIN
        
        
SITE_CACHE[settings.SITE_ID] = CurrentSite()

