"""Default site content classes."""


from cms.apps.pages import content


class Content(content.Content):
    
    """The default page content associated by default with all pages."""
    
    # Class meta information.
    
    # You must mark one, and only one content class as default. This will be the default option for newly-created pages.
    use_as_default = True  
    
    # You must mark one, and only one content class base base. This will be used as the base class for built-in CMS content classes.
    use_as_base = True
    
    verbose_name_plural = "content"
    
    # Fields used in this content class.
    
    content_primary = content.HtmlField("primary content",
                                        required=False)
    
    def get_fieldsets(self):
        """Returns the admin fieldsets."""
        return (("Page content", {"fields": ("content_primary",)}),)