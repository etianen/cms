"""Content types used by the news application."""


import datetime

from django.conf import settings
from django.contrib.syndication.feeds import Feed
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage
from django.http import Http404
from django.utils.dates import MONTHS

from cms.apps.pages import content
from cms.apps.pages.feeds import registered_feeds
from cms.apps.pages.models import Page
from cms.apps.events.models import Event


class EventsFeed(content.Content):
    
    """An archive of published news articles."""
    
    icon = settings.CMS_MEDIA_URL + "img/content-types/events-feed.png"
    
    events_per_page = content.PositiveIntegerField(required=True,
                                                   default=10)
    
    def get_feed_url(self):
        """Returns the URL of the RSS feed for this page."""
        return reverse("feeds", kwargs={"url": EVENT_FEED_KEY}) + unicode(self.page.id) + "/"
        
    feed_url = property(get_feed_url,
                        doc="The URL of the RSS feed for this page.")
    
    def render_to_response(self, request, template_name, context, **kwargs):
        """Renders the given page."""
        # Generate list of available years.
        try:
            first_event = self.published_events.order_by("start_date")[0]
            last_event = self.published_events.order_by("-start_date")[0]
        except IndexError:
            available_years = []
        else:
            available_years = range(first_event.start_date.year, last_event.start_date.year + 1)
        year_archives = [{"year": year, "url": self.reverse("year_archive", year)} for year in available_years]
        context.setdefault("year_archives", year_archives)
        # Generate the feed URL.
        context.setdefault("feed_url", self.feed_url)
        return super(EventsFeed, self).render_to_response(request, template_name, context, **kwargs)
    
    def get_published_events(self):
        """Returns all the published events for this events feed."""
        return Event.published_objects.filter(events_feed=self.page)
    
    published_events = property(get_published_events,
                                doc="All the published events for this events feed.")
    
    def get_page(self, request, events):
        """Returns an object paginator for the given events."""
        page = request.GET.get(settings.PAGINATION_KEY, 1)
        try:
            page = int(page)
        except ValueError:
            raise Http404, "'%s' is not a valid page number." % page 
        paginator = Paginator(events, self.events_per_page)
        try:
            page = paginator.page(page)
        except EmptyPage:
            raise Http404, "There are no articles on this page."
        return page
    
    @content.view(r"^$")
    def index(self, request):
        """Generates a page of the upcoming events."""
        now = datetime.datetime.now()
        all_events = self.published_events.filter(start_date__gte=now.date())
        events = self.get_page(request, all_events)
        context = {"events": events}
        return self.render_to_response(request, "events/event_list.html", context)
    
    @content.view(r"^(\d+)/$")
    def year_archive(self, request, year):
        """Generates a page showing the articles in a given year."""
        year = int(year)
        all_events = self.published_events.filter(start_date__year=year)
        events = self.get_page(request, all_events)
        context = {"events": events,
                   "title": "Archive for %i" % year,
                   "short_title": year,
                   "year": year}
        return self.render_to_response(request, "events/event_list.html", context)
    
    @content.view(r"^(\d+)/(\d+)/$")
    def month_archive(self, request, year, month):
        """Generates a page showing the articles in a given year."""
        year = int(year)
        month = int(month)
        all_events = self.published_events.filter(start_date__year=year,
                                                  start_date__month=month)
        events = self.get_page(request, all_events)
        breadcrumbs = self.breadcrumbs + [{"url": self.reverse("year_archive", year), "title": year},]
        context = {"events": events,
                   "title": u"Archive for %s %i" % (MONTHS[month], year),
                   "short_title": MONTHS[month],
                   "breadcrumbs": breadcrumbs,
                   "year": year,
                   "month": month}
        return self.render_to_response(request, "events/event_list.html", context)
    
    @content.view(r"^(\d+)/(\d+)/([a-zA-Z0-9_\-]+)/$")
    def event_detail(self, request, year, month, event_slug):
        """Dispatches to the article detail page."""
        year = int(year)
        month = int(month)
        all_events = self.page.event_set.all().filter(start_date__year=year,
                                                      start_date__month=month)
        try:
            event = all_events.get(url_title=event_slug)
        except Event.DoesNotExist:
            raise Http404, "An event with a URL title of '%s' does not exist." % event_slug
        breadcrumbs = self.breadcrumbs + [{"url": self.reverse("year_archive", year), "title": year},
                                          {"url": self.reverse("month_archive", year, month), "title": MONTHS[month]},]
        context = {"breadcrumbs": breadcrumbs}
        return self.render_page(event, request, "events/event_detail.html", context)    
    
    
content.register(EventsFeed)


EVENT_FEED_KEY = "events"


class EventsRSSFeed(Feed):
    
    """Feed generator for articles."""
    
    def get_object(self, bits):
        """Allows customization of the feed."""
        if len(bits) == 0:
            return None
        elif len(bits) == 1:
            return Page.published_objects.get(id=bits[0])
        else:
            raise ObjectDoesNotExist
        
    def title(self, obj=None):
        """Generates the feed title."""
        homepage = Page.objects.get_homepage()
        site_title = homepage.browser_title or homepage.title
        if obj is None:
            return "%s Latest Events" % site_title
        return obj.title

    def link(self, obj=None):
        if obj is None:
            return "/"
        return obj.url

    def description(self, obj=None):
        """Generates the feed description."""
        homepage = Page.objects.get_homepage()
        site_title = homepage.browser_title or homepage.title
        return "Latest events from %s." % site_title
        
    def items(self, obj=None):
        """Generates the feed items."""
        events = Event.published_objects.all()
        if obj is not None:
            events = events.filter(events_feed=obj)
        events = events.order_by("-start_date", "-id")[:settings.FEED_LENGTH]
        return events
    
    
registered_feeds[EVENT_FEED_KEY] = EventsRSSFeed

