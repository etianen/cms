"""URLs used by the events application."""


from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("cms.apps.events.views",
                       url(r"^$", "index", name="index"),
                       url(r"^page/(\d+)/$", "index", name="index_paginated"),)


ARTICLE_SET_ATTR = "event_set"
ARTICLES_PER_PAGE_ATTR = "events_per_page"
ARTICLE_DATE_ATTR = "start_date"
LIST_NAME = "events"

BASE_KWARGS = {"article_set_attr": ARTICLE_SET_ATTR,
               "articles_per_page_attr": ARTICLES_PER_PAGE_ATTR,
               "article_date_attr": ARTICLE_DATE_ATTR,
               "list_name": LIST_NAME}

YEAR_ARCHIVE_KWARGS = {"template_name": "events/year_archive.html"}
YEAR_ARCHIVE_KWARGS.update(BASE_KWARGS)

MONTH_ARCHIVE_KWARGS = {"template_name": "events/month_archive.html"}
MONTH_ARCHIVE_KWARGS.update(BASE_KWARGS)

ARTICLE_DETAIL_KWARGS = {"article_set_attr": ARTICLE_SET_ATTR,
                         "article_date_attr": ARTICLE_DATE_ATTR,
                         "article_name": "event",
                         "template_name": "events/event_detail.html"}

RSS_KWARGS = {"article_set_attr": ARTICLE_SET_ATTR,
              "article_date_attr": ARTICLE_DATE_ATTR}


urlpatterns += patterns("cms.apps.news.views",
                       
                        url(r"^(\d{4})/$", "year_archive", YEAR_ARCHIVE_KWARGS, name="year_archive"),
                        url(r"^(\d{4})/page/(\d+)/$", "year_archive", YEAR_ARCHIVE_KWARGS, name="year_archive_paginated"),
                       
                        url(r"^(\d{4})/(\d{1,2})/$", "month_archive", MONTH_ARCHIVE_KWARGS, name="month_archive"),
                        url(r"^(\d{4})/(\d{1,2})/page/(\d+)/$", "month_archive", MONTH_ARCHIVE_KWARGS, name="month_archive_paginated"),
                       
                        url(r"^(\d{4})/(\d{1,2})/([a-zA-Z0-9_\-]+)/$", "article_detail", ARTICLE_DETAIL_KWARGS, name="event_detail",),
                        
                        url(r"^rss/$", "rss", RSS_KWARGS, name="rss"),)

