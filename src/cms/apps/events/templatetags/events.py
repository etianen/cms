"""Template tags used to render feed articles."""


from django import template

from cms.apps.pages.models import Page
from cms.apps.pages.templatetags import PatternNode


register = template.Library()


@register.tag
def upcoming_events(parser, token):
    """Renders a list of the upcoming events."""
    def handler(context, feed, count=5):
        # Get the page reference.
        try:
            feed = Page.objects.get_page(feed)
        except Page.DoesNotExist:
            return ""
        # Get the events.
        events = feed.event_set.all()[:count]
        # Render the template.
        context.push()
        try:
            context.update({"events": events,
                            "feed": feed})
            return template.loader.render_to_string("events/upcoming_events.html", context)
        finally:
            context.pop()
    return PatternNode(parser, token, handler, ("{feed} {count}", "{feed}",))

