"""Optional external libraries that enhance the CMS."""

from django.conf import settings

from cms import loader


class External(object):
    
    """An optional external library."""
    
    def __init__(self, app_name):
        """Initializes the external."""
        self._app_name = app_name
        
    def __bool__(self):
        """Returns if the app is installed."""
        return self._app_name in settings.INSTALLED_APPS
    
    def _load_object(self, name):
        """Loads the named object from the external library."""
        try:
            return loader.load_object(".".join((self._app_name, name)))
        except (ImportError, AttributeError):
            return object
    
    def __getattr__(self, name):
        """Loads the named object from the external library."""
        return self._load_object(name)
    
    def __getitem__(self, name):
        """Loads the named object from the external library."""
        return self._load_object(name)


reversion = External("reversion")

watson = External("watson")