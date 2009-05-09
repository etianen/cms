#!/usr/bin/env python
"""
Management script for this site.

For an explanation of this script, and information about all available
subcommands, please see the Django documentation at:

<http://docs.djangoproject.com/en/dev/ref/django-admin/>

By default, this script will run using the `settings` module found within
this package.  To use a different flavour of settings file, set the
environmental variable DJANGO_SETTINGS_FLAVOUR.  For example, setting the
variable to 'debug' will cause the `settings_debug` module to be loaded instead.

For local development machines, the 'local' flavour of settings file is
recommended. 
"""


import os, sys

from django.core.management import execute_manager


# Derive the settings module name from the environmental variables.


if "DJANGO_SETTINGS_MODULE" in os.environ:
    settings_module_name = os.environ["DJANGO_SETTINGS_MODULE"]
else:
    settings_module_name = "settings"
    if "DJANGO_SETTINGS_FLAVOUR" in os.environ:
        settings_module_name = os.environ.get("DJANGO_SETTINGS_MODULE", "settings")
        settings_flavour = os.environ["DJANGO_SETTINGS_FLAVOUR"]
        settings_module_name = "%s_%s" % (settings_module_name, settings_flavour)


# Perform a dynamic import of the settings module.

settings_module = __import__(settings_module_name, {}, {}, [""])


if __name__ == "__main__":
    execute_manager(settings_module)

