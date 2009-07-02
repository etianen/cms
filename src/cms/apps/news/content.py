"""Content types used by the news application."""


import datetime

from django.conf import settings
from django.utils.feedgenerator import DefaultFeed
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, EmptyPage
from django.http import Http404, HttpResponse
from django.utils.dates import MONTHS

from cms.apps.pages import content
from cms.apps.pages.models import Page
from cms.apps.news.models import Article
from cms.apps.pages.sites import add_domain
from cms.apps.pages.templatetags.pages import html


class FeedBase(content.Content):
    
    """Base class for content that renders date-based fields."""

    # Set this to a short string for the RSS feed path.
    feed_slug = None
    
    # Set this to the subclass of ArticleBase that is rendered by this feed.
    article_model = None
    
    # Set this to the date field used to order the article model.
    date_field = "publication_date"
    
    items_per_page = content.PositiveIntegerField(required=True,
                                                  default=10)
    
    def get_published_articles(self):
        """Returns all the published articles for this feed."""
        return self.article_model.published_objects.filter(feed=self.page)
    
    published_articles = property(get_published_articles,
                                  doc="All the published articles for this feed.")
    
    def get_page(self, request, articles):
        """Returns an object paginator for the given articles."""
        page = request.GET.get(settings.PAGINATION_KEY, 1)
        try:
            page = int(page)
        except ValueError:
            raise Http404, "'%s' is not a valid page number." % page 
        paginator = Paginator(articles, self.items_per_page)
        try:
            page = paginator.page(page)
        except EmptyPage:
            raise Http404, "There are no articles on this page."
        return page
    
    @content.view(r"^$")
    def index(self, request):
        """Generates a page of the latest news articles."""
        now = datetime.datetime.now()
        all_articles = self.published_articles
        articles = self.get_page(request, all_articles)
        context = {"articles": articles,
                   "year": now.year}
        return self.render_to_response(request, "%s/article_list.html" % self.feed_slug, context)
    
    @content.view(r"^rss/$")
    def rss(self, request):
        """Generates an RSS feed for this feed."""
        page = self.page
        generator = DefaultFeed(title=page.title,
                                link=add_domain(page.url),
                                description=page.meta_description)
        for article in self.article_model.published_objects.order_by("-%s" % self.date_field, "-pk")[:settings.FEED_LENGTH]:
            pubdate = getattr(article, self.date_field)
            if isinstance(pubdate, datetime.date):
                pubdate = datetime.datetime(pubdate.year, pubdate.month, pubdate.day)
            generator.add_item(title=article.title,
                               link=add_domain(article.url),
                               description=html(article.content or article.summary),
                               pubdate=pubdate,
                               unique_id=unicode(article.pk))
        return HttpResponse(generator.writeString("utf-8"))
    
    @content.view(r"^(\d+)/$")
    def year_archive(self, request, year):
        """Generates a page showing the articles in a given year."""
        year = int(year)
        all_articles = self.published_articles.filter(**{"%s__year" % self.date_field: year})
        articles = self.get_page(request, all_articles)
        context = {"articles": articles,
                   "title": "Archive for %i" % year,
                   "short_title": year,
                   "year": year}
        return self.render_to_response(request, "%s/article_list.html" % self.feed_slug, context)
    
    @content.view(r"^(\d+)/(\d+)/$")
    def month_archive(self, request, year, month):
        """Generates a page showing the articles in a given year."""
        year = int(year)
        month = int(month)
        all_articles = self.published_articles.filter(**{"%s__year" % self.date_field: year,
                                                         "%s__month" % self.date_field: month})
        articles = self.get_page(request, all_articles)
        breadcrumbs = self.breadcrumbs + [{"url": self.reverse("year_archive", year), "title": year},]
        context = {"articles": articles,
                   "title": u"Archive for %s %i" % (MONTHS[month], year),
                   "short_title": MONTHS[month],
                   "breadcrumbs": breadcrumbs,
                   "year": year,
                   "month": month}
        return self.render_to_response(request, "%s/article_list.html" % self.feed_slug, context)
    
    @content.view(r"^(\d+)/(\d+)/([a-zA-Z0-9_\-]+)/$")
    def article_detail(self, request, year, month, article_slug):
        """Dispatches to the article detail page."""
        year = int(year)
        month = int(month)
        all_articles = self.article_model.objects.filter(**{"feed": self.page,
                                                            "%s__year" % self.date_field: year,
                                                            "%s__month" % self.date_field: month})
        try:
            article = all_articles.get(url_title=article_slug)
        except self.article_model.DoesNotExist:
            raise Http404, "An article with a URL title of '%s' does not exist." % article_slug
        breadcrumbs = self.breadcrumbs + [{"url": self.reverse("year_archive", year), "title": year},
                                          {"url": self.reverse("month_archive", year, month), "title": MONTHS[month]},]
        context = {"breadcrumbs": breadcrumbs}
        return self.render_page(article, request, "%s/article_detail.html" % self.feed_slug, context)


class NewsFeed(FeedBase):
    
    """An archive of published news articles."""
    
    feed_slug = "news"
    
    article_model = Article
    
    icon = settings.CMS_MEDIA_URL + "img/content-types/news-feed.png"
    
    
content.register(NewsFeed)
    
