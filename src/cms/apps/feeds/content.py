"""Base content classes for feed-based content."""


import datetime

from django import template
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.syndication.feeds import Feed
from django.core.paginator import Paginator, EmptyPage
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.utils.dates import MONTHS

from cms.apps.feeds import registered_feeds
from cms.apps.pages.templatetags.pages import html
from cms.apps.pages.models import Page
from cms.apps.pages import content


class FeedMetaClass(content.ContentMetaClass):
    
    """Auto-registers feed content models with the syndication framework."""
    
    def __init__(self, name, bases, attrs):
        """Initializes the FeedMetaClass."""
        super(FeedMetaClass, self).__init__(name, bases, attrs)
        if self.feed_key:
            class ArticleFeed(ArticleFeedBase):
                content_cls = self
            registered_feeds[self.feed_key] = ArticleFeed


class FeedBase(content.Content):
    
    """Base class for content that renders date-based fields."""

    __metaclass__ = FeedMetaClass

    classifier = "feeds"

    # Set this to the subclass of ArticleBase that is rendered by this feed.
    article_model = None
    
    # Set this to the date field used to order the article model.
    date_field = None
    
    # The number of items to publish in the RSS feed.
    feed_length = 30
    
    # The key under which the RSS feed is registered.
    feed_key = None
    
    article_list_template = "feeds/article_list.html"
    
    article_detail_template = "feeds/article_detail.html"
    
    article_archive_template = "feeds/article_archive.html"
    
    latest_articles_template = "feeds/latest_articles.html"
    
    items_per_page = content.PositiveIntegerField(default=10)
    
    def render_page(self, page, request, template, context, **kwargs):
        """Renders the given page."""
        context.setdefault("article_type_plural", self.article_model._meta.verbose_name_plural)
        if self.feed_key:
            feed_url = reverse("feeds", kwargs={"url": self.feed_key}) + unicode(self.page.permalink or self.page.id) + u"/"
            context.setdefault("feed_url", feed_url)
        return super(FeedBase, self).render_page(page, request, template, context, **kwargs)
    
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
    
    def get_articles(self):
        """Returns all articles of this feed."""
        return self.article_model.objects.filter(feed=self.page)
    
    articles = property(get_articles,
                        doc="All articles of this feed.")
    
    def get_latest_articles(self):
        """Returns the list of articles for the latest article feeds."""
        return self.articles
        
    latest_articles = property(lambda self: self.get_latest_articles(),
                               doc="The list of articles for the latest article feeds.")
    
    @content.view(r"^$")
    def index(self, request):
        """Generates a page of the latest news articles."""
        now = datetime.datetime.now()
        all_articles = self.latest_articles
        articles = self.get_page(request, all_articles)
        context = {"articles": articles,
                   "year": now.year}
        return self.render_to_response(request, self.article_list_template, context)
    
    @content.view(r"^(\d{4})/$")
    def year_archive(self, request, year):
        """Generates a page showing the articles in a given year."""
        year = int(year)
        all_articles = self.articles.filter(**{"%s__year" % self.date_field: year})
        articles = self.get_page(request, all_articles)
        context = {"articles": articles,
                   "title": "Archive for %i" % year,
                   "short_title": year,
                   "year": year}
        return self.render_to_response(request, self.article_list_template, context)
    
    @content.view(r"^(\d{4})/(\d{1,2})/$")
    def month_archive(self, request, year, month):
        """Generates a page showing the articles in a given year."""
        year = int(year)
        month = int(month)
        all_articles = self.articles.filter(**{"%s__year" % self.date_field: year,
                                               "%s__month" % self.date_field: month})
        articles = self.get_page(request, all_articles)
        breadcrumbs = self.breadcrumbs + [content.Breadcrumb(year, self.reverse("year_archive", year))]
        context = {"articles": articles,
                   "title": u"Archive for %s %i" % (MONTHS[month], year),
                   "short_title": MONTHS[month],
                   "breadcrumbs": breadcrumbs,
                   "year": year,
                   "month": month}
        return self.render_to_response(request, self.article_list_template, context)
    
    @content.view(r"^(\d{4})/(\d{1,2})/([a-zA-Z0-9_\-]+)/$")
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
        breadcrumbs = self.breadcrumbs + [content.Breadcrumb(year, self.reverse("year_archive", year)),
                                          content.Breadcrumb(MONTHS[month], self.reverse("month_archive", year, month))]
        context = {"breadcrumbs": breadcrumbs,
                   "year": getattr(article, self.date_field).year}
        return self.render_page(article, request, self.article_detail_template, context)


class ArticleFeedBase(Feed):
    
    """A feed of articles."""
    
    description_template = "feeds/article_description.html"
    
    def __init__(self, *args, **kwargs):
        """Initializes the ArticleFeedBase."""
        super(ArticleFeedBase, self).__init__(*args, **kwargs)
        self.homepage = Page.objects.get_homepage()
    
    def get_object(self, bits):
        """Allows customization of the feed."""
        if len(bits) == 0:
            return None
        elif len(bits) == 1:
            # Accept integer page id or permalink.
            try:
                page_id = int(bits[0])
            except ValueError:
                page_id = bits[0]
            return Page.objects.get_page(page_id)
        else:
            raise ObjectDoesNotExist
        
    def title(self, obj=None):
        """Generates the feed title."""
        site_title = self.homepage.browser_title or self.homepage.title
        if obj is None:
            title = u"Latest %s" % self.content_cls.article_model._meta.verbose_name_plural.title()
        else:
            title = obj.browser_title or obj.title
        context = {"is_homepage": False,
                   "site_title": site_title,
                   "browser_title": title}
        return template.loader.render_to_string("browser_title.html", context)

    def link(self, obj):
        if obj is None:
            return "/"
        return obj.url

    def description(self, obj):
        """Generates the feed description."""
        if obj is None:
            return self.homepage.meta_description
        return obj.meta_description
        
    def items(self, obj):
        """Generates the feed items."""
        content_cls = self.content_cls
        articles = content_cls.article_model.objects.order_by("-%s" % content_cls.date_field, "-pk")
        if obj:
            articles = articles.filter(feed=obj)
        return articles[:content_cls.feed_length]

