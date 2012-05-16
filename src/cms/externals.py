"""Optional external libraries that enhance the CMS."""

from contextlib import contextmanager

from django.conf import settings

from cms import loader


class External(object):
    
    """An optional external library."""
    
    def __init__(self, app_name):
        """Initializes the external."""
        self._app_name = app_name
        
    def __nonzero__(self):
        """Returns if the app is installed."""
        return self._app_name in settings.INSTALLED_APPS
    
    def _load(self, name):
        """
        Loads the named object from the external library.
        
        If the object is not present, and ImportError or an
        Attribute error will be raised.
        """
        if self:
            return loader.load_object(".".join((self._app_name, name)))
        raise ImportError
    
    def load_class(self, name, fallback=None):
        """
        Loads the named class from the external library.
        
        If the object is not present, the fallback class will
        be returned
        """
        try:
            return self._load(name)
        except (ImportError, AttributeError):
            if fallback is None:
                return object
            return fallback
    
    def __getattr__(self, name):
        """Loads the named class from the external library."""
        return self.load_class(name)
    
    def __getitem__(self, name):
        """Loads the named class from the external library."""
        return self.load_class(name)
    
    def load_method(self, name, fallback=None):
        """
        Loads the named method from the external library.
        
        If the method is not present, a no-op dummy method
        will be returned.
        """
        try:
            return self._load(name)
        except (ImportError, AttributeError):
            if fallback is None:
                return lambda *args, **kwargs: None
            return fallback
        
    def __call__(self, _name, *args, **kwargs):
        """
        Calls the named method in the external library.
        
        If the method is not present, this is a no-op.
        """
        self.load_method(_name)(*args, **kwargs)
       
    def context_manager(self, name, fallback=None):
        """
        Returns the named context manager from the external library.
        
        If the context manager is not present, a no-op dummy context
        manager will be returned.
        """
        try:
            return self._load(name)
        except (ImportError, AttributeError):
            if fallback is None:
                @contextmanager
                def context_manager(*args, **kwargs):
                    yield
                return context_manager
            return fallback


reversion = External("reversion")

watson = External("watson")

historylinks = External("historylinks")