"""Specialized settings for importing data into MySQL."""


from staging import *


DATABASE_OPTIONS = {"init_command": "SET foreign_key_checks = 0;",}

