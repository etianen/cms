"""Some useful optimization routines."""


from functools import wraps


def instance_cache(func):
    """
    Caches the result of the function call in the instance.
    
    This garuntees that the given function will be called a maximum of once per
    instance.  The function may not accept any arguments.
    """
    cache_name = func.__name__ + "_cache"
    @wraps(func)
    def func_(obj):
        if not hasattr(obj, cache_name):
            result = func(obj)
            setattr(obj, cache_name, result)
        return getattr(obj, cache_name)
    return func_

