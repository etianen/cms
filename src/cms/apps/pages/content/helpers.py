"""Some template helper classes."""


class Breadcrumb(object):
    
    """
    An entry in the breadcrumb trail.
    
    This conforms to the same interface as Page, allowing both to be used
    as entries in the breadcrumb trail.
    """
    
    def __init__(self, title, url):
        """Initializes the Breadcrumb."""
        self.title = title
        self.url = url
    
    def __unicode__(self):
        """Returns the title of the NavEntry."""
        return unicode(self.title)
        
        
class NavEntry(Breadcrumb):
    
    """
    An entry in the site navigation.
    
    This conforms to the same interface as Page, allowing both to be used
    as entries in the site navigation.
    """
    
    def __init__(self, title, url, navigation=None):
        """Initializes the NavEntry."""
        super(NavEntry, self).__init__(title, url)
        self.navigation = navigation or ()