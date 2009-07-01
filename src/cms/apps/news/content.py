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
from cms.apps.news.models import Article


class NewsFeed(content.Content):
    
    """An archive of published news articles."""
    
    icon = settings.CMS_MEDIA_URL + "img/content-types/news-feed.png"
    
    articles_per_page = content.PositiveIntegerField(required=True,
                                                     default=10)
    
    def get_feed_url(self):
        """Returns the URL of the RSS feed for this page."""
        return reverse("feeds", kwargs={"url": ARTICLE_FEED_KEY}) + unicode(self.page.id) + "/"
        
    feed_url = property(get_feed_url,
                        doc="The URL of the RSS feed for this page.")
    
    def render_page(self, page, request, template_name, context, **kwargs):
        """Renders the given page."""
        # Generate list of available years.
        available_months = self.published_articles.dates("publication_date", "month")
        news_archive = []
        year = None
        for date in available_months:
            month = date.month
            if date.year != year:
                year = date.year
                news_archive.append({"year": year, "months": [], "url": self.reverse("year_archive", year)})
            news_archive[-1]["months"].append({"month": MONTHS[month], "url": self.reverse("month_archive", year, month)})
        context.setdefault("news_archive", news_archive)
        # Generate the feed URL.
        context.setdefault("feed_url", self.feed_url)
        return super(NewsFeed, self).render_page(page, request, template_name, context, **kwargs)
    
    def get_published_articles(self):
        """Returns all the published articles for this news feed."""
        return Article.published_objects.filter(news_feed=self.page)
    
    published_articles = property(get_published_articles,
                                  doc="All the published articles for this news feed.")
    
    def get_page(self, request, articles):
        """Returns an object paginator for the given articles."""
        page = request.GET.get(settings.PAGINATION_KEY, 1)
        try:
            page = int(page)
        except ValueError:
            raise Http404, "'%s' is not a valid page number." % page 
        paginator = Paginator(articles, self.articles_per_page)
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
        return self.render_to_response(request, "news/base.html", context)
    
    @content.view(r"^(\d+)/$")
    def year_archive(self, request, year):
        """Generates a page showing the articles in a given year."""
        year = int(year)
        all_articles = self.published_articles.filter(publication_date__year=year)
        articles = self.get_page(request, all_articles)
        context = {"articles": articles,
                   "title": "Archive for %i" % year,
                   "short_title": year,
                   "year": year}
        return self.render_to_response(request, "news/base.html", context)
    
    @content.view(r"^(\d+)/(\d+)/$")
    def month_archive(self, request, year, month):
        """Generates a page showing the articles in a given year."""
        year = int(year)
        month = int(month)
        all_articles = self.published_articles.filter(publication_date__year=year,
                                                      publication_date__month=month)
        articles = self.get_page(request, all_articles)
        breadcrumbs = self.breadcrumbs + [{"url": self.reverse("year_archive", year), "title": year},]
        context = {"articles": articles,
                   "title": u"Archive for %s %i" % (MONTHS[month], year),
                   "short_title": MONTHS[month],
                   "breadcrumbs": breadcrumbs,
                   "year": year,
                   "month": month}
        return self.render_to_response(request, "news/base.html", context)
    
    @content.view(r"^(\d+)/(\d+)/([a-zA-Z0-9_\-]+)/$")
    def article_detail(self, request, year, month, article_slug):
        """Dispatches to the article detail page."""
        year = int(year)
        month = int(month)
        all_articles = self.page.article_set.all().filter(publication_date__year=year,
                                                          publication_date__month=month)
        try:
            article = all_articles.get(url_title=article_slug)
        except Article.DoesNotExist:
            raise Http404, "An article with a URL title of '%s' does not exist." % article_slug
        breadcrumbs = self.breadcrumbs + [{"url": self.reverse("year_archive", year), "title": year},
                                          {"url": self.reverse("month_archive", year, month), "title": MONTHS[month]},]
        context = {"breadcrumbs": breadcrumbs,
                   "year": article.publication_date.year,
                   "month": article.publication_date.month}
        return self.render_page(article, request, "news/article_detail.html", context)    
    
    
content.register(NewsFeed)


ARTICLE_FEED_KEY = "news"


class NewsRSSFeed(Feed):
    
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
            return "%s Latest News" % site_title
        return obj.title

    def link(self, obj=None):
        if obj is None:
            return "/"
        return obj.url

    def description(self, obj=None):
        """Generates the feed description."""
        homepage = Page.objects.get_homepage()
        site_title = homepage.browser_title or homepage.title
        return "Latest news from %s." % site_title
        
    def items(self, obj=None):
        """Generates the feed items."""
        articles = Article.published_objects.all()
        if obj is not None:
            articles = articles.filter(news_feed=obj)
        articles = articles.order_by("-publication_date", "-id")[:settings.FEED_LENGTH]
        return articles
    
    
registered_feeds[ARTICLE_FEED_KEY] = NewsRSSFeed

