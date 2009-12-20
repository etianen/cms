"""Some useful iteration tools."""


def iteritems(object):
    """
    Iterates over the items in an object.
    
    Both dictionary and two-tuple iterables are supported.
    """
    if hasattr(object, "iteritems"):
        return object.iteritems()
    if hasattr(object, "items"):
        return iter(object.items())
    return iter(object)
    
    