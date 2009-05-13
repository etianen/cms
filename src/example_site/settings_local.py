"""
Settings for local development.

These settings are not fast or efficient, but allow local servers to be run
using the manage.py utility.
"""


import os

from settings_debug import *


# Save media files to the uploads directory in the user's home folder.

MEDIA_ROOT = os.path.expanduser("~/Uploads/%s" % SITE_DOMAIN)


# Static media serving

STATIC_MEDIA += ((SITE_MEDIA_URL, SITE_MEDIA_ROOT),
                 (CMS_MEDIA_URL, CMS_MEDIA_ROOT),
                 (MEDIA_URL, MEDIA_ROOT))


# Enable serving of static media files (slow, not for production).

SERVE_STATIC_MEDIA = True


# Disable prepending www, as local servers run from localhost.

PREPEND_WWW = False

