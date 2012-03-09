#!/usr/bin/env python

"""
Starts a new CMS project with the given name.
"""

import sys

from django.core import management


def start_cms_project():
    argv = list(sys.argv)
    if len(argv) != 2:
        raise management.CommandError("start_cms_project accepts one argument - the name of the project to create.")
    management.call_command("startproject",
        argv[1],
        template = "~/Workspace/cms/src/cms/project_template/",
        n = "py,css,html",
    )


if __name__ == "__main__":
    start_cms_project()