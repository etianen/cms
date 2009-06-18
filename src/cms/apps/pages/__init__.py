"""
Page management application.

This forms the core of the CMS functionality.
"""


from cms.apps.pages import content


# Automatically scan installed apps for content models.
content.autodiscover()

