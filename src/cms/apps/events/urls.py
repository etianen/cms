"""URLs used by the events application."""


from django.conf.urls.defaults import patterns, url

from cms.apps.events.models import Event


FEED_KWARGS = {"queryset": Event.objects.all(),
               "publication_date_field": "start_date",
               "expiry_date_field": "end_date"}


urlpatterns = patterns("cms.apps.feeds.views",
                       
                       url(r"^$", "upcoming_index", FEED_KWARGS, name="upcoming_index"),
                       url(r"^page/(\d+)/$", "upcoming_index", FEED_KWARGS, name="upcoming_index_paginated"),
                       
                       url(r"^(\d{4})/$", "archive_year", FEED_KWARGS, name="archive_year"),
                       url(r"^(\d{4})/page/(\d+)/$", "archive_year", FEED_KWARGS, name="archive_year_paginated"),
                       
                       url(r"^(\d{4})/(\d{1,2})/$", "archive_month", FEED_KWARGS, name="archive_month"),
                       url(r"^(\d{4})/(\d{1,2})/page/(\d+)/$", "archive_month", FEED_KWARGS, name="archive_month_paginated"),
                       
                       url(r"^(\d{4})/(\d{1,2})/([a-zA-Z0-9_\-]+)/$", "object_detail", FEED_KWARGS, name="object_detail",),
                       
                       url(r"^rss/$", "rss", FEED_KWARGS, name="rss"),)

