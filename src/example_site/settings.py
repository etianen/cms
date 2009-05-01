"""
Site-specific settings file.

For an explanation of these settings, please see the Django documentation at:

<http://docs.djangoproject.com/en/dev/>
"""


import os

from cms.settings import *


# Database settings.

DATABASE_ENGINE = "mysql"

DATABASE_NAME = ""

DATABASE_USER = DATABASE_NAME

DATABASE_PASSWORD = ""


# Absolute paths to the directory where all media files are stored.

MEDIA_ROOT = ""

MEDIA_URL = "/media/"


# Whether to automatically add www to the start of the domain name.  

PREPEND_WWW = True


# Debug settings.  These should be set to False in a production environment.

DEBUG = False

TEMPLATE_DEBUG = False


# Error reporting settings.  Use these to set up automatic error notifications.

ADMINS = (("Etianen.com Error Reporting", "errors@etianen.com"),)

MANAGERS = ()

SEND_BROKEN_LINK_EMAILS = False


# Locale settings.

TIME_ZONE = "Europe/London"

LANGUAGE_CODE = "en-gb"

USE_I18N = False


# A list of additional installed applications.

INSTALLED_APPS += ()


# Absolute path to the directory containing this project.

PROJECT_ROOT = os.path.dirname(__file__)


# Absolute paths to the directory where site-specific media files are stored.

SITE_MEDIA_ROOT = os.path.join(PROJECT_ROOT, "media")

SITE_MEDIA_URL = MEDIA_URL + "site/"


# Absolute URL of the location where admin media files are served.

ADMIN_MEDIA_PREFIX = MEDIA_URL + "admin/"


# Absolute URL of the location where CMS media files are served.

CMS_MEDIA_URL = MEDIA_URL = "cms/"


# Absolute path to the directory where templates are stored.

TEMPLATE_ROOT = os.path.join(PROJECT_ROOT, "templates")

TEMPLATE_DIRS += (TEMPLATE_ROOT,)

