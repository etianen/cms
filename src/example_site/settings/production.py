"""
Site-specific settings file.

For an explanation of these settings, please see the Django documentation at:

<http://docs.djangoproject.com/en/dev/>

While many of these settings assume sensible defaults, you must provide values
for the site, database, media and email sections below.
"""


import hashlib, os  # @UnusedImport

from cms.settings import *  # @UnusedWildImport


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

INSTALLED_APPS += ("cms.apps.news",)


# The base content type to use for all CMS apps.

DEFAULT_CONTENT = "cms.apps.pages.content.Content"


# A list of registered contact form types.

CONTACT_FORMS = (("contact", "cms.apps.contact.forms.ContactForm"),)


# Absolute path to the directory containing this project.

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


# Absolute path to the directory where site-specific media files are stored.

SITE_MEDIA_ROOT = os.path.join(PROJECT_ROOT, "media")

SITE_MEDIA_URL = MEDIA_URL + "site/"

TINYMCE_CONTENT_CSS = SITE_MEDIA_URL + "css/content.css"


# Absolute URL of the location where admin media files are served.

ADMIN_MEDIA_PREFIX = MEDIA_URL + "admin/"


# Absolute URL of the location where CMS media files are served.

CMS_MEDIA_URL = MEDIA_URL + "cms/"


# Absolute path to the directory where templates are stored.

TEMPLATE_ROOT = os.path.join(PROJECT_ROOT, "templates")

TEMPLATE_DIRS = (TEMPLATE_ROOT,) + TEMPLATE_DIRS


# Namespace for cache keys, if using a process-shared cache.

CACHE_MIDDLEWARE_KEY_PREFIX = SITE_DOMAIN


# A secret key used for cryptographic algorithms.  For convenience, this is
# generated from your site domain, database password and email password.  If,
# for some reason, these are not considered secure, you can override it below.

SECURE_SETTINGS = (SITE_DOMAIN, DATABASE_PASSWORD, EMAIL_HOST_PASSWORD)

SECRET_KEY = hashlib.sha1("".join(SECURE_SETTINGS)).hexdigest()