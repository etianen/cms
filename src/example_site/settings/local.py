"""
Settings for local development.

These settings are not fast or efficient, but allow local servers to be run
using the django-admin.py utility.
"""


import os  # @UnusedImport

from production import *  # @UnusedWildImport


# Run in debug mode.

DEBUG = True

TEMPLATE_DEBUG = DEBUG

MEDIA_DEBUG = DEBUG


# Save media files to the uploads directory in the user's home folder.

MEDIA_ROOT = os.path.expanduser("~/Sites/%s/media" % SITE_DOMAIN)


# Use local server.

SITE_DOMAIN = "localhost:8000"


# Enable serving of static media files (slow, not for production).

SERVE_STATIC_MEDIA = True


# Disable prepending www, as local servers run from localhost.

PREPEND_WWW = False


# Optional separate database settings

#DATABASE_NAME = ""

#DATABASE_USER = ""

#DATABASE_PASSWORD = ""


# Optional separate email settings.

#EMAIL_HOST = "smtp.gmail.com"

#EMAIL_HOST_USER = ""

#EMAIL_HOST_PASSWORD = ""

#EMAIL_PORT = 587

#EMAIL_USE_TLS = True