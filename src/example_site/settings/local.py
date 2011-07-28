"""
Settings for local development.

These settings are not fast or efficient, but allow local servers to be run
using the django-admin.py utility.
"""


import os

from production import *


# Run in debug mode.

DEBUG = True

TEMPLATE_DEBUG = DEBUG


# Save media files to the uploads directory in the user's home folder.

MEDIA_ROOT = os.path.expanduser("~/Sites/%s/media" % SITE_DOMAIN)

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"


# Use local server.

SITE_DOMAIN = "localhost:8000"


# Disable prepending www, as local servers run from localhost.

PREPEND_WWW = False


# Disable the template cache for development.

TEMPLATE_LOADERS = (
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
)


# Optional separate database settings

#DATABASES["default"]["NAME"] = ""

#DATABASES["default"]["USER"] = ""

#DATABASES["default"]["PASSWORD"] = ""