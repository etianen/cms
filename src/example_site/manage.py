#!/usr/bin/env python
import os, importlib

from django.core.management import execute_manager


def main():
    submodule = os.environ.get("DJANGO_SETTINGS_SUBMODULE", "production")
    site_package = os.path.split(os.path.abspath(os.path.dirname(__file__)))[-1]
    settings_name = ".".join((site_package, "settings", submodule))
    settings = importlib.import_module(settings_name)
    execute_manager(settings)


if __name__ == "__main__":
    main()