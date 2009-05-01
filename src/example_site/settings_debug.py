"""
Site-specific debug settings.

This are not appropriate for a production environment, but are great for getting
things to work a staging site.
"""


from settings import *


# Debug settings are enabled, allowing full stack traces to be displayed in the
# browser.

DEBUG = True

TEMPLATE_DEBUG = True


# Many staging sites don't have the www prefix, so URL rewriting is disabled.

PREPEND_WWW = False

