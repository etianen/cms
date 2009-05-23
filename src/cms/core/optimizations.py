"""Some useful optimization routines."""


from functools import wraps


def cached_property(fget, fset=None, fdel=None, doc=None):
    """Creates a property who's method calls are cached."""
    cache_name = fget.__name__ + "_cache"
    @wraps(fget)
    def fget_(self):
        if not hasattr(self, cache_name):
            result = fget(self)
            setattr(self, cache_name, result)
        return getattr(self, cache_name)
    if fset:
        @wraps(fset)
        def fset_(self, value):
            setattr(self, cache_name, value)
            fset(self, value)
    else:
        fset_ = None
    if fdel:
        @wraps(fdel)
        def fdel_(self):
            delattr(self, cache_name)
            fdel(self)
    else:
        fdel_ = None
    return property(fget_, fset_, fdel_, doc)

