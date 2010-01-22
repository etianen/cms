"""URLs used by the news application."""


from django.conf.urls.defaults import patterns, url

from cms.apps.news.models import Article


FEED_KWARGS = {"queryset": Article.objects.all()}


urlpatterns = patterns("cms.apps.feeds.views",
                       
                       url(r"^$", "archive_index", FEED_KWARGS, name="archive_index"),
                       url(r"^page/(\d+)/$", "archive_index", FEED_KWARGS, name="archive_index_paginated"),
                       
                       url(r"^(\d{4})/$", "archive_year", FEED_KWARGS, name="archive_year"),
                       url(r"^(\d{4})/page/(\d+)/$", "archive_year", FEED_KWARGS, name="archive_year_paginated"),
                       
                       url(r"^(\d{4})/(\d{1,2})/$", "archive_month", FEED_KWARGS, name="archive_month"),
                       url(r"^(\d{4})/(\d{1,2})/page/(\d+)/$", "archive_month", FEED_KWARGS, name="archive_month_paginated"),
                       
                       url(r"^(\d{4})/(\d{1,2})/([a-zA-Z0-9_\-]+)/$", "object_detail", FEED_KWARGS, name="object_detail",),
                       
                       url(r"^rss/$", "rss", FEED_KWARGS, name="rss"),)

