"""Database utilities."""

import warnings
from contextlib import contextmanager

from django.conf import settings
from django.db import connections
from django.db.utils import DEFAULT_DB_ALIAS


@contextmanager
def locked(*models, **kwargs):
    database_name = kwargs.pop("database_name", DEFAULT_DB_ALIAS)
    connection = connections[database_name]
    engine_name = settings.DATABASES[database_name]["ENGINE"]
    if engine_name == "django.db.backends.mysql":
        cursor = connection.cursor()
        cursor.execute("LOCK TABLES {0}".format(", ".join("`{0}` WRITE".format(model._meta.db_table) for model in models)))
        try:
            yield
        finally:
            cursor.execute("UNLOCK TABLES")
    else:
        warnings.warn("Cannot lock tables for engine {0}".format(engine_name))
        yield