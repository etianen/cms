"""Views used by the events application."""


import datetime

from django.http import Http404
from django.core import paginator
from django.db.models import Q


def index(request, page_number="1"):
    """Generates a page of the upcoming events."""
    page = request.page
    content = page.content
    event_set = page.event_set
    # Paginate the events.
    now = datetime.datetime.now()
    all_events = event_set.filter(Q(start_date__gte=now) | Q(end_date__gte=now))
    try:
        events = paginator.Paginator(all_events, content.events_per_page).page(page_number)
    except paginator.InvalidPage:
        raise Http404, "There are no events to display"
    # Render the template.
    date = datetime.datetime.now()
    dates = event_set.dates("start_date", "month")
    context = {"events": events,
               "date": date,
               "dates": dates}
    return page.render_to_response(request, "events/index.html", context)

