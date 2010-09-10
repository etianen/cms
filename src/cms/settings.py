"""
Base settings for the CMS.

Individual sites may override these settings by creating their own settings
file.  It is recommended that you import these base settings into your custom
settings file using the following syntax:

>>> from cms.settings import *

An example site-specific settings file is included with this distribution.
Please see `example_site.settings` for more information.

For an explanation of these settings, please see the Django documentation at:

<http://docs.djangoproject.com/en/dev/>
"""


import os


# Absolute path to the directory containing the CMS.

CMS_ROOT = os.path.dirname(__file__)


# Absolute path to the directory containing the CMS media files.

CMS_MEDIA_ROOT = os.path.join(CMS_ROOT, "media")


# Static media serving.

MEDIA_DEBUG = False


# Database settings.

DATABASE_ENGINE = "mysql"


# Template settings.

TEMPLATE_LOADERS = ("django.template.loaders.filesystem.load_template_source",
                    "django.template.loaders.app_directories.load_template_source",)

TEMPLATE_DIRS = (os.path.join(CMS_ROOT, "templates",),)

TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
                               "django.core.context_processors.debug",
                               "django.core.context_processors.i18n",
                               "django.core.context_processors.media",
                               "django.contrib.messages.context_processors.messages",
                               "django.core.context_processors.request",
                               "cms.core.context_processors.site",
                               "cms.core.context_processors.media",
                               "cms.core.context_processors.conf",
                               "cms.apps.pages.context_processors.page",)


# Dispatch settings.

MIDDLEWARE_CLASSES = ("django.middleware.transaction.TransactionMiddleware",
                      "django.middleware.common.CommonMiddleware",
                      "django.contrib.sessions.middleware.SessionMiddleware",
                      "django.contrib.messages.middleware.MessageMiddleware",
                      "django.contrib.auth.middleware.AuthenticationMiddleware",
                      "cms.apps.pages.middleware.PageMiddleware",)

ROOT_URLCONF = "cms.urls"


# Application settings.

INSTALLED_APPS = ("django.contrib.contenttypes",
                  "django.contrib.sessions",
                  "django.contrib.auth",
                  "django.contrib.admin",
                  "django.contrib.sitemaps",
                  "django.contrib.sites",
                  "django.contrib.messages",
                  "reversion",
                  "cms.core",
                  "cms.apps.pages",
                  "cms.apps.media",)


# Multi-site settings.

SITE_ID = 1


# Publication settings.

PUBLICATION_PREVIEW_KEY = "preview"


# SEO settings.

SEO_PRIORITIES = ((1.0, "Very high"),
                  (0.8, "High"),
                  (0.5, "Medium"),
                  (0.3, "Low"),
                  (0.0, "Very low"),)


# Internationalization settings.

USE_I18N = False


# Staff management settings.

DEFAULT_GROUP_IDS = (1,)