"""Template tags used by the site search application."""


from django import template

from cms.apps.pages.templatetags import PatternNode
from cms.apps.pages.models import Page


register = template.Library()


@register.tag
def search_form(parser, token):
    """Renders the Google Custom Search Engine search form."""
    def handler(context, search_page, form_id="cse-search-box"):
        request = context["request"]
        search_term = request.GET.get("q", "")
        search_page = Page.objects.get_page(search_page)
        context.push()
        try:
            context.update({"search_page": search_page,
                            "form_id": form_id,
                            "search_term": search_term})
            return template.loader.render_to_string("search/form.html", context)
        finally:
            context.pop()
    return PatternNode(parser, token, handler, ("{search_page} {form_id}", "{search_page}",))

