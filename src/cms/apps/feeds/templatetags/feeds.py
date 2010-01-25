"""Template tags used to render feed articles."""


from django import template
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.text import truncate_words

from cms.apps.pages.models import Page
from cms.apps.pages.templatetags import PatternNode


register = template.Library()


@register.tag
def article_list(parser, token):
    """Renders the given articles as a list."""
    def handler(context, summary_length=100):
        page = context["page"]
        content = page.content
        article_model = content.article_model
        # Render the template.
        context.push()
        try:
            context.update({"verbose_name": article_model._meta.verbose_name,
                            "verbose_name_plural": article_model._meta.verbose_name_plural})
            template_names = ("%s/article_list.html" % article_model._meta.app_label,
                              "feeds/article_list.html")
            return template.loader.render_to_string(template_names, context)
        finally:
            context.pop()
    return PatternNode(parser, token, handler, ("",))


@register.tag
def date_archive(parser, token):
    """Renders a list of the latest news articles."""
    def handler(context):
        page = context["page"]
        content = page.content
        article_model = content.article_model
        articles = content.get_articles()
        dates = articles.dates(article_model.date_field_name, "month")
        # Render the template.
        context.push()
        try:
            context.update({"dates": dates,
                            "verbose_name": article_model._meta.verbose_name,
                            "verbose_name_plural": article_model._meta.verbose_name_plural})
            template_names = ("%s/date_archive.html" % article_model._meta.app_label,
                              "feeds/date_archive.html")
            return template.loader.render_to_string(template_names, context)
        finally:
            context.pop()
    return PatternNode(parser, token, handler, ("",))


@register.tag
def latest_articles(parser, token):
    """Renders a list of the latest news articles."""
    def handler(context, feed, count=5):
        # Get the page reference.
        try:
            feed = Page.objects.get_page(feed)
        except Page.DoesNotExist:
            return ""
        content = feed.content
        article_model = content.article_model
        # Get the articles.
        articles = content.get_latest_articles()[:count]
        # Render the template.
        context.push()
        try:
            context.update({"articles": articles,
                            "feed": feed})
            template_names = ("%s/latest_articles.html" % article_model._meta.app_label,
                              "feeds/latest_articles.html")
            return template.loader.render_to_string(template_names, context)
        finally:
            context.pop()
    return PatternNode(parser, token, handler, ("{feed} {count}", "{feed}",))

