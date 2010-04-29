"""Default site content classes."""


from cms.apps.pages import content


class Content(content.Content):
    
    """The default page content associated by default with all pages."""
    
    # Class meta information.
    
    # If True, this will be used as the default content for newly-created pages.
    # Only one content class may be used as default.
    use_as_default = True  
    
    use_as_base = True
    
    verbose_name_plural = "content"
    
    # Fields used in this content class.
    
    content_primary = content.HtmlField("primary content",
                                        required=False)
    
    def get_fieldsets(self):
        """Returns the admin fieldsets."""
        return (("Page content", {"fields": ("content_primary",)}),)