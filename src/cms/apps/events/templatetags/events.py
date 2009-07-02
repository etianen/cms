"""Template tags used by the events application."""


import datetime

from django import template
from django.utils.dates import MONTHS

from cms.apps.events.models import Event
from cms.apps.pages.templatetags import Library 


register = Library()


@register.inclusion_tag("events/upcoming_events.html")
def upcoming_events(count=5):
    """Renders a list of the upcoming events."""
    now = datetime.datetime.now()
    events = Event.published_objects.filter(start_date__gte=now.date())[:count]
    context = {"events": events}
    return context


@register.context_tag
def events_archive(context, page, year):
    """Renders the events archive for the given page."""
    page_content = page.content
    request = context["request"]
    available_months = page_content.published_events.dates("start_date", "month")
    # Generate the news archive.
    events_archive = []
    year = None
    for date in available_months:
        month = date.month
        if date.year != year:
            year = date.year
            events_archive.append({"year": year, "months": [], "url": page_content.reverse("year_archive", year)})
        events_archive[-1]["months"].append({"month": MONTHS[month], "url": page_content.reverse("month_archive", year, month)})
    # Generate the context.
    context = {"request": request,
               "page": page,
               "year": year,
               "events_archive": events_archive}
    return template.loader.render_to_string("events/events_archive.html", context)