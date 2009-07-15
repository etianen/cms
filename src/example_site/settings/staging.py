"""
Site specific staging settings.

These are suitable for powering a staging version of the site, running off a
subdomain.
"""


from debug import *


# Use local server.

SITE_DOMAIN = "staging." + SITE_DOMAIN


# Disable prepending www, as staging servers frequenty run off a subdomain.

PREPEND_WWW = False


# Ensure that MySQL creates INNODB tables.

DATABASE_OPTIONS = {"init_command": "SET storage_engine=INNODB",}


# Optional separate media root.

# MEDIA_ROOT = "/var/uploads/%s" % SITE_DOMAIN


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

