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

STATICFILES_DIRS = (
    ("cms", os.path.join(CMS_ROOT, "media")),
)


# Template settings.

TEMPLATE_LOADERS = (
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

TEMPLATE_DIRS = (os.path.join(CMS_ROOT, "templates",),)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    "cms.core.context_processors.conf",
    "cms.core.context_processors.pages",
)


# Dispatch settings.

MIDDLEWARE_CLASSES = (
    "django.middleware.transaction.TransactionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    'django.middleware.csrf.CsrfViewMiddleware',
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "cms.apps.historylinks.middleware.HistoryLinkFallbackMiddleware",
    "cms.core.middleware.PreviewMiddleware",
    "cms.core.middleware.PageMiddleware",
)

ROOT_URLCONF = "cms.urls"


# Application settings.

INSTALLED_APPS = (
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.auth",
    "django.contrib.admin",
    "django.contrib.sitemaps",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "optimizations",
    "reversion",
    "usertools",
    "cms.core",
    "cms.apps.historylinks",
    "cms.apps.pages",
    "cms.apps.media",
)

PAGE_BACKEND = "cms.apps.pages.backend.PageBackend"


# Multi-site settings.

SITE_ID = 1


# Publication settings.

PUBLICATION_PREVIEW_KEY = "preview"


# SEO settings.

SEO_PRIORITIES = (
    (1.0, "Very high"),
    (0.8, "High"),
    (0.5, "Medium"),
    (0.3, "Low"),
    (0.0, "Very low"),
)


# Internationalization settings.

USE_I18N = False

USE_L10N = True