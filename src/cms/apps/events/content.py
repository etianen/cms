"""Content types used by the news application."""


import datetime

from django.conf import settings
from django.contrib.syndication.feeds import Feed
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage
from django.http import Http404
from django.utils.dates import MONTHS

from cms.apps.pages import content
from cms.apps.pages.models import Page
from cms.apps.news.content import FeedBase
from cms.apps.events.models import Event


class EventsFeed(FeedBase):
    
    """An archive of published news articles."""
    
    article_model = Event
    
    date_field = "start_date"
    
    icon = settings.CMS_MEDIA_URL + "img/content-types/events-feed.png"
    
    article_list_template = ("events/article_list.html", "news/article_list.html",)
    
    article_detail_template = ("events/article_detail.html", "news/article_detail.html",)
    
    article_archive_template = ("events/article_archive.html", "news/article_archive.html",)
    
    @content.view(r"^$")
    def index(self, request):
        """Generates a page of the upcoming events."""
        now = datetime.datetime.now()
        all_events = self.published_articles.filter(start_date__gte=now.date())
        events = self.get_page(request, all_events)
        context = {"articles": events,
                   "year": now.year}
        return self.render_to_response(request, self.article_list_template, context)
    
    
content.register(EventsFeed)

