"""Navigation utilities."""

from django import template

from cms.core.templatetags import PatternNode


register = template.Library()


@register.tag
def navigation(parser, token):
    """
    Renders a navigation list for the given pages.
    
    The pages should all be a subclass of PageBase, and possess a get_absolute_url() method.
    
    You can also specify an alias for the navigation, at which point it will be set in the
    context rather than rendered.
    """
    def handler(context, pages, alias=None):
        request = context["request"]
        entries = []
        # Compile the entries.
        for page in pages:
            url = page.get_absolute_url()
            entries.append({
                "short_title": unicode(page),
                "title": page.title,
                "here": request.path.startswith(url),
                "url": url
            })
        # Set to alias, maybe.
        if alias:
            context[alias] = entries
            return ""
        # Render the template.
        context.push()
        try:
            context.update({
                "navigation": entries
            })
            return template.loader.render_to_string("navigation.html", context)
        finally:
            context.pop()
    return PatternNode(parser, token, handler, (
        "{pages} {alias}",
        "{pages}",
    ))