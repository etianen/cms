"""
Dynamic class loading routines.

Why isn't this in the Python standard library?  Why does Django re-implement it
a million times?  Most odd.
"""


def load_module(name):
    """Loads a module by name."""
    return __import__(name, {}, {}, [""])


def load_object(name):
    """Loads an object from a module."""
    module_name, object_name = name.rsplit(".", 1)
    module = load_module(module_name)
    return getattr(module, object_name)