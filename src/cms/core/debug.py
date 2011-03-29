"""Debug helpers."""

import traceback
from functools import wraps

from django.conf import settings


def print_exc(func):
    """
    Decorator that prints any raised exceptions to stdout, but only when in debug mode.
    
    This is useful for catching those pesky errors that Django would otherwise squeltch.
    """
    if settings.DEBUG:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except:
                traceback.print_exc()
                raise
        return wrapper
    else:
        return func
        
        
def print_current_exc():
    """Prints the current exception, if in debug model"""
    if settings.DEBUG:
        traceback.print_exc()