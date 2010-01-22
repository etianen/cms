"""Template tags used to render feed articles."""


from django import template
from django.utils.text import truncate_html_words

from cms.apps.pages.templatetags import PatternNode
from cms.apps.pages.templatetags.pages import html


register = template.Library()


@register.tag
def article_list(parser, token):
    """Renders the given articles as a list."""
    def handler(context, summary_length=100):
        page = context["page"]
        content = page.content
        article_model = content.article_model
        articles = context["articles"].object_list
        # Generate the article list.
        article_list = []
        for article in articles:
            summary = html(article.summary or truncate_html_words(article.content, summary_length))
            article_list.append({"short_title": article.short_title or article.title,
                                 "title": article.title,
                                 "url": article.get_absolute_url(),
                                 "is_featured": article.is_featured,
                                 "date": getattr(article, content.publication_date_field),
                                 "summary": summary,
                                 "article": article})
        # Render the template.
        context.push()
        try:
            context.update({"articles": article_list})
            template_names = ("%s/article_list.html" % article_model._meta.app_label,
                              "feeds/article_list.html")
            return template.loader.render_to_string(template_names, context)
        finally:
            context.pop()
    return PatternNode(parser, token, handler, ("{summary_length}", ""))


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

