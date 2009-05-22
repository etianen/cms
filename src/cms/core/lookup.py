"""Utilities for looking up Python objects by name."""


def get_module(name):
    """Returns a Python module by name."""
    return __import__(name, {}, {}, [""])


def get_object(name):
    """Returns a Python object by name."""
    module_name, object_name = name.rsplit(".", 1)
    module = get_module(module_name)
    obj = getattr(module, object_name)
    return obj

