"""Simple static content page."""


from cms.apps.pages import content


class SimpleContent(content.Content):
    
    verbose_name = "content"
    
    
content.register(SimpleContent, "content")

