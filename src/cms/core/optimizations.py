"""Some useful optimization routines."""


from functools import wraps


def get_cache_name(func):
    """Generates a string name for a function result cache."""
    return func.__name__ + "_cache"


def cache_getter(func):
    """
    Caches the result of the function call in the instance.
    
    This garuntees that the given function will be called a maximum of once per
    instance.  The function may not accept any arguments.
    """
    cache_name = get_cache_name(func)
    @wraps(func)
    def func_(obj):
        if not hasattr(obj, cache_name):
            result = func(obj)
            setattr(obj, cache_name, result)
        return getattr(obj, cache_name)
    return func_


def cache_setter(getter):
    """
    Ensures that a setter updates the value of a getter decorated with
    instance_cache,
    """
    cache_name = get_cache_name(getter)
    def decorator(func):
        @wraps(func)
        def func_(obj, value):
            result = func(obj, value)
            setattr(obj, cache_name, value)
            return result
        return func_
    return decorator

