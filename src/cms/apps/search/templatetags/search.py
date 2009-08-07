"""Template tags used by the site search application."""


from cms.apps.pages.templatetags import Library
from cms.apps.pages.models import Page


register = Library()


@register.inclusion_tag("search/form.html", takes_context=True)
def search_form(context, search_page, form_id="cse-search-box"):
    """Renders the Google Custom Search Engine search form."""
    request = context["request"]
    search_term = request.GET.get("q", "")
    search_page = Page.objects.get_page(search_page)
    context = {"search_page": search_page,
               "form_id": form_id,
               "search_term": search_term}
    return context

