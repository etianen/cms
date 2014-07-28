"""
Settings for local development.

These settings are not fast or efficient, but allow local servers to be run
using the django-admin.py utility.

This file should be excluded from version control to keep the settings local.
"""

import os.path

from production import SITE_DOMAIN


# Run in debug mode.

DEBUG = True

TEMPLATE_DEBUG = DEBUG


# Save media files to the user's Sites folder.

MEDIA_ROOT = os.path.expanduser(os.path.join("~/Sites" + SITE_DOMAIN + "media"))

STATIC_ROOT = os.path.expanduser(os.path.join("~/Sites" + SITE_DOMAIN + "static"))


# Use local server.

SITE_DOMAIN = "localhost:8000"

PREPEND_WWW = False


# Disable the template cache for development.

TEMPLATE_LOADERS = (
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
)


# Local database settings

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "HOST": "localhost",
        "NAME": "{{ project_name }}",
        "USER": "{{ user }}",
        "PASSWORD": "",
    },
}


# Optional console-based email backend.

#EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
