#!/usr/bin/env python
"""
Management script for this site.

For an explanation of this script, and information about all available
subcommands, please see the Django documentation at:

<http://docs.djangoproject.com/en/dev/ref/django-admin/> 
"""


import sys

from django.core.management import execute_manager


import settings


if __name__ == "__main__":
    execute_manager(settings)

