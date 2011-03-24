"""Views used by the pages app."""

from django.views.generic import TemplateView

from cms.apps.pages import content


class ContentIndexView(TemplateView):
    
    """Displays the index page for a page."""
    
    def get_template_names(self):
        """Returns the list of template names."""
        content_cls = content.lookup(self.request.pages.current.content_type)
        return (
            "pages/{0}.html".format(content_cls.__name__.lower()),
            "pages/base.html",
        )