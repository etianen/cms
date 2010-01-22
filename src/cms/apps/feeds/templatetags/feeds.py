"""Template tags used to render feed articles."""


from django import template

from cms.apps.pages.templatetags import PatternNode


register = template.Library()


@register.tag
def date_archive(parser, token):
    """Renders a list of the latest news articles."""
    def handler(context):
        page = context["page"]
        content = page.content
        article_model = content.article_model
        articles = content.get_articles()
        dates = articles.dates(content.publication_date_field, "month")
        # Render the template.
        context.push()
        try:
            context.update({"dates": dates})
            template_names = ("%s/date_archive.html" % article_model._meta.app_label,
                              "feeds/date_archive.html")
            return template.loader.render_to_string(template_names, context)
        finally:
            context.pop()
    return PatternNode(parser, token, handler, ("",))

