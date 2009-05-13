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

STATIC_MEDIA = ()

SERVE_STATIC_MEDIA = False


# Database settings.

DATABASE_ENGINE = "mysql"


# Template settings.

TEMPLATE_LOADERS = ("django.template.loaders.filesystem.load_template_source",
                    "django.template.loaders.app_directories.load_template_source",)

TEMPLATE_DIRS = (os.path.join(CMS_ROOT, "templates",),)

TEMPLATE_CONTEXT_PROCESSORS = ("django.core.context_processors.auth",
                               "django.core.context_processors.request",
                               "django.core.context_processors.media",
                               "cms.core.context_processors.site",
                               "cms.core.context_processors.media",)


# Dispatch settings.

MIDDLEWARE_CLASSES = ("django.middleware.transaction.TransactionMiddleware",
                      "django.middleware.common.CommonMiddleware",
                      "django.contrib.sessions.middleware.SessionMiddleware",
                      "django.contrib.auth.middleware.AuthenticationMiddleware",)

ROOT_URLCONF = "cms.urls"


# Application settings.

INSTALLED_APPS = ("django.contrib.auth",
                  "django.contrib.contenttypes",
                  "django.contrib.sessions",
                  "django.contrib.admin",)


# SEO settings.

SEO_PRIORITIES = ((1.0, "Very high"),
                  (0.8, "High"),
                  (0.5, "Medium"),
                  (0.3, "Low"),
                  (0.0, "Very low"),)

SEO_DEFAULT_PRIORITY = None

SEO_CHANGE_FREQUENCIES = (("always", "Always"),
                          ("hourly", "Hourly"),
                          ("daily", "Daily"),
                          ("weekly", "Weekly"),
                          ("monthly", "Monthly"),
                          ("yearly", "Yearly"),
                          ("never", "Never"))

SEO_DEFAULT_CHANGE_FREQUENCY = None


# Internationalization settings.

USE_I18N = False

