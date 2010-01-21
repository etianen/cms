"""Template tags used to render feed articles."""


from django import template

from cms.apps.pages.models import Page
from cms.apps.pages.templatetags import PatternNode


register = template.Library()


@register.tag
def latest_articles(parser, token):
    """Renders a list of the latest news articles."""
    def handler(context, feed, count=5):
        # Get the page reference.
        try:
            feed = Page.objects.get_page(feed)
        except Page.DoesNotExist:
            return ""
        # Get the articles.
        articles = feed.article_set.all()[:count]
        # Render the template.
        context.push()
        try:
            context.update({"articles": articles,
                            "feed": feed})
            return template.loader.render_to_string("news/latest_articles.html", context)
        finally:
            context.pop()
    return PatternNode(parser, token, handler, ("{feed} {count}", "{feed}",))

