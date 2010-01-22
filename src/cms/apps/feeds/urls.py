"""URLs used by the news application."""


from django.conf.urls.defaults import patterns, url


urlpatterns = patterns("cms.apps.feeds.views",
                       
                       url(r"^$", "index", name="index"),
                       url(r"^page/(\d+)/$", "index", name="index_paginated"),
                       
                       url(r"^(\d{4})/$", "year_archive", name="year_archive"),
                       url(r"^(\d{4})/page/(\d+)/$", "year_archive", name="year_archive_paginated"),
                       
                       url(r"^(\d{4})/(\d{1,2})/$", "month_archive", name="month_archive"),
                       url(r"^(\d{4})/(\d{1,2})/page/(\d+)/$", "month_archive", name="month_archive_paginated"),
                       
                       url(r"^(\d{4})/(\d{1,2})/([a-zA-Z0-9_\-]+)/$", "article_detail", name="article_detail",),
                       
                       url(r"^rss/$", "rss", name="rss"),)

