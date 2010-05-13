"""Custom content classes."""


from cms.apps.pages import content


class Content(content.Content):
    
    content_primary = content.HtmlField("primary content",
                                        required=False)
    
    use_as_default = True
    
    use_as_base = True
    
    def get_fieldsets(self):
        """Returns the fieldsets used to lay out the content form."""
        return (("Page content", {"fields": ("content_primary",)}),)