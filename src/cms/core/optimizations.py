"""Some useful optimization routines."""

from functools import wraps


class _CachedProperty(object):

    """A property who's value is cached on the object."""
    
    def __init__(self, f_get, f_set=None, f_del=None):
        """Initializes the cached property."""
        self.getter(f_get)
        if callable(f_set):
            self.setter(f_set)
        if callable(f_del):
            self.deleter(f_del)
        
    def getter(self, f_get):
        """Decorator that specifies the getter function for this property."""
        self._f_get = f_get
        # Store the property name.
        self._property_name = f_get.__name__
        # Store the cache name.
        self._cache_name = "_{name}_cache".format(
            name = f_get.__name__,
        )
        return self
            
    def setter(self, f_set):
        """Decorator that specifies the setter function for this property."""
        self._f_set = f_set
        return self
        
    def deleter(self, f_del):
        """Decorator that specifies the deleter function for this property."""
        self._f_del = f_del
        return self
        
    def __get__(self, obj, cls):
        """Accessor for this property."""
        # Access via class.
        if obj is None:
            return self
        # Access via obj.
        if hasattr(obj, self._cache_name):
            return getattr(obj, self._cache_name)
        # Generate the value to cache.
        value = self._f_get(obj)
        setattr(obj, self._cache_name, value)
        return value
        
    def __set__(self, obj, value):
        """Setter for this property."""
        if callable(self._f_set):
            self._f_set(obj, value)
            # Store the cached value.
            cache_name = self._cache_name
            setattr(obj, self._cache_name, value)
        else:
            raise AttributeError("{name} is a read-only property".format(
                name = self._property_name,
            ))
        
    def __delete__(self, obj):
        """Deleter for this property."""
        if callable(self._f_del):
            self._f_del(obj)
            # Clear the cache.
            delattr(obj, self._cache_name)
        else:
            raise AttributeError("{name} is a read-only property".format(
                name = self._property_name,
            ))
            

# Public name for the cached propert decorator. Using a class as a decorator just looks plain ugly. :P            
cached_property = _CachedProperty