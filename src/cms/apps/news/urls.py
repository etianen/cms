"""URLs used by the CMS news app."""

from django.conf.urls import patterns, url

from cms.apps.news import views


urlpatterns = patterns("cms.apps.news.views",
    
    url(r"^$", views.ArticleArchiveView.as_view(), name="article_archive"),
    
    url(r"^feed/$", views.ArticleFeedView.as_view(), name="article_feed"),
    
    url("^(?P<year>\d+)/$", views.ArticleYearArchiveView.as_view(), name="article_year_archive"),
    
    url("^(?P<year>\d+)/(?P<month>\w+)/$", views.ArticleMonthArchiveView.as_view(), name="article_month_archive"),
    
    url("^(?P<year>\d+)/(?P<month>\w+)/(?P<day>\d+)/$", views.ArticleDayArchiveView.as_view(), name="article_day_archive"),
    
    url("^(?P<year>\d+)/(?P<month>\w+)/(?P<day>\d+)/(?P<url_title>[^/]+)/$", views.ArticleDetailView.as_view(), name="article_detail"),
    
    url("^(?P<url_title>[^/]+)/$", views.ArticleCategoryArchiveView.as_view(), name="article_category_archive"),
    
)