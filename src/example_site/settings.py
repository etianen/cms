"""
Site-specific settings file.

For an explanation of these settings, please see the Django documentation at:

<http://docs.djangoproject.com/en/dev/>

While many of these settings assume sensible defaults, you must provide values
for the site, database, media and email sections below.
"""


import hashlib, os

from cms.settings import *


# The name of this site.  Used for branding in the online admin area.

SITE_NAME = "Example Site"

SITE_DOMAIN = "example.com"


# Database settings.

DATABASE_NAME = ""

DATABASE_USER = DATABASE_NAME

DATABASE_PASSWORD = ""


# Absolute path to the directory where all uploaded media files are stored.

MEDIA_ROOT = "/var/uploads/%s" % SITE_DOMAIN

MEDIA_URL = "/media/"


# Email settings.

EMAIL_HOST = ""

EMAIL_HOST_USER = ""

EMAIL_HOST_PASSWORD = ""

EMAIL_PORT = 25

EMAIL_USE_TLS = False

SERVER_EMAIL = "notifications@" + SITE_DOMAIN

DEFAULT_FROM_EMAIL = SERVER_EMAIL

EMAIL_SUBJECT_PREFIX = "[%s] " % SITE_NAME


# Template settings.

PAGE_TEMPLATE_AREAS = ("main", "sidebar",)


# Whether to automatically add www to the start of the domain name.  

PREPEND_WWW = True


# Error reporting settings.  Use these to set up automatic error notifications.

ADMINS = (("Etianen.com Error Reporting", "errors@etianen.com"),)

MANAGERS = ()

SEND_BROKEN_LINK_EMAILS = False


# Locale settings.

TIME_ZONE = "Europe/London"

LANGUAGE_CODE = "en-gb"


# A list of additional installed applications.

INSTALLED_APPS += ()


# Absolute path to the directory containing this project.

PROJECT_ROOT = os.path.dirname(__file__)


# Absolute path to the directory where site-specific media files are stored.

SITE_MEDIA_ROOT = os.path.join(PROJECT_ROOT, "media")

SITE_MEDIA_URL = MEDIA_URL + "site/"


# Absolute URL of the location where admin media files are served.

ADMIN_MEDIA_PREFIX = MEDIA_URL + "admin/"


# Absolute URL of the location where CMS media files are served.

CMS_MEDIA_URL = MEDIA_URL + "cms/"


# Absolute path to the directory where templates are stored.

TEMPLATE_ROOT = os.path.join(PROJECT_ROOT, "templates")

TEMPLATE_DIRS += (TEMPLATE_ROOT,)


# Namespace for cache keys, if using a process-shared cache.

CACHE_MIDDLEWARE_KEY_PREFIX = SITE_DOMAIN


# A secret key used for cryptographic algorithms.  For convenience, this is
# generated from your site domain, database password and email password.  If,
# for some reason, these are not considered secure, you can override it below.

SECURE_SETTINGS = (SITE_DOMAIN, DATABASE_PASSWORD, EMAIL_HOST_PASSWORD)

SECRET_KEY = hashlib.sha1("".join(SECURE_SETTINGS)).hexdigest()

