#!/usr/bin/env python

"""
Starts a new CMS project with the given name.
"""

import os
import sys

from django.core import management


def start_cms_project():
    argv = list(sys.argv)
    if len(argv) != 2:
        raise management.CommandError("start_cms_project accepts one argument - the name of the project to create.")
    management.call_command("startproject",
        argv[1],
        template = "{}/../project_template/".format(os.path.dirname( __file__ )),
        n = "py,css,html,gitignore",
    )


if __name__ == "__main__":
    start_cms_project()
