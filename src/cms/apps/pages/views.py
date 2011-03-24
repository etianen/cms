"""Views used by the pages app."""

from django.contrib.contenttypes.models import ContentType
from django.views.generic import TemplateView


class ContentIndexView(TemplateView):
    
    """Displays the index page for a page."""
    
    def get_template_names(self):
        """Returns the list of template names."""
        content_cls = ContentType.objects.get_for_id(self.request.pages.current.content_type_id).model_class()
        return (
            "pages/{0}.html".format(content_cls.__name__.lower()),
            "pages/base.html",
        )