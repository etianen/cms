"""Default site content classes."""


from cms.apps.pages import content


class Content(content.Content):
    
    """The default page content associated by default with all pages."""
    
    # Class meta information.
    
    use_as_default = True  
    
    use_as_base = True
    
    verbose_name_plural = "content"
    
    # Fields used in this content class.
    
    content_primary = content.HtmlField("primary content",
                                        required=False)
    
    def get_fieldsets(self):
        """Returns the admin fieldsets."""
        return (("Page content", {"fields": ("content_primary",)}),)