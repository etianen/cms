"""Some useful optimization routines."""


from functools import wraps


def get_cache_name(func):
    """Generates a cache name for a function."""
    func_name = func.__name__
    # Clean up the function name (assumes standard function naming conventions).
    if func_name.startswith("get_") or func_name.startswith("set_") or func_name.startswith("del_"):
        func_name = func_name[4:]
    return "_%s_cache" % func_name
    
    
def cached_getter(func):
    """Ensures that the result of the wrapped getter method is cached in the instance."""
    cache_name = get_cache_name(func)
    @wraps(func)
    def func_(obj):
        if not hasattr(obj, cache_name):
            result = func(obj)
            setattr(obj, cache_name, result)
        return getattr(obj, cache_name)
    return func_
        
        
def cached_setter(getter):
    """Ensures that the getter cache is updated with new values from the wrapped setter."""
    cache_name = get_cache_name(getter)
    def decorator(func):
        @wraps(func)
        def func_(obj, value):
            func(obj, value)
            setattr(obj, cache_name, value)
        return func_
    return decorator


def cached_deleter(getter):
    """Ensures that the getter cache is deleted when the wrapped deleter is called."""
    cache_name = get_cache_name(getter)
    def decorator(func):
        @wraps(func)
        def func_(obj):
            func(obj)
            delattr(obj, cache_name)
        return func_
    return decorator

