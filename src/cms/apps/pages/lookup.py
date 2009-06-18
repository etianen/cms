"""Utilities for looking up Python objects by name."""


def get_module(name):
    """Looks up the named Python module."""
    return __import__(name, {}, {}, [""])


def get_object(name):
    """Looks up the named Python object."""
    module_name, obj_name = name.rsplit(".", 1)
    module = get_module(module_name)
    obj = getattr(module, obj_name)
    return obj

