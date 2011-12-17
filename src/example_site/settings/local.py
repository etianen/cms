"""
Settings for local development.

These settings are not fast or efficient, but allow local servers to be run
using the django-admin.py utility.

This file should be excluded from version control to keep the settings local.
"""
#@PydevCodeAnalysisIgnore

import os.path

from production import SITE_DOMAIN, DATABASES


# Run in debug mode.

DEBUG = True

TEMPLATE_DEBUG = DEBUG


# Save media files to the user's Sites folder.

MEDIA_ROOT = os.path.expanduser("~/Sites/%s/media" % SITE_DOMAIN)

STATIC_ROOT = os.path.expanduser("~/Sites/%s/static" % SITE_DOMAIN)


# Use local server.

SITE_DOMAIN = "localhost:8000"


# Disable the template cache for development.

TEMPLATE_LOADERS = (
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
)


# Optional separate database settings

#DATABASES["default"]["NAME"] = ""

#DATABASES["default"]["USER"] = ""

#DATABASES["default"]["PASSWORD"] = ""


# Optional console-based email backend.

#EMAIL_BACKEND = "django.core.mail.backends.dummy.EmailBackend"