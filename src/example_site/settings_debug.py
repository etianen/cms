"""
Site-specific debug settings.

This are not appropriate for a production environment, but are great for getting
things to work a staging site.
"""


from settings import *


# Debug settings are enabled, allowing full stack traces to be displayed in the
# browser.

DEBUG = True

TEMPLATE_DEBUG = DEBUG

