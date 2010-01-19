"""Base content classes for feed-based content."""


import datetime

from django import template
from django.contrib.syndication.feeds import Feed
from django.core.urlresolvers import reverse
from django.http import Http404

from cms.apps.feeds import registered_feeds
from cms.apps.pages.models import Page
from cms.apps.pages import content


DefaultContent = content.get_default_content()


class FeedBase(DefaultContent):
    
    """Base class for content that renders date-based fields."""

    abstract = True

    classifier = "feeds"

    # Set this to the subclass of ArticleBase that is rendered by this feed.
    article_model = None
    
    # Set this to the date field used to order the article model.
    date_field = None
    
    # The number of items to publish in the RSS feed.
    feed_length = 30
    
    article_list_template = "feeds/article_list.html"
    
    year_archive_template = "feeds/year_archive.html"
    
    month_archive_template = "feeds/month_archive.html"
    
    article_detail_template = "feeds/article_detail.html"
    
    article_archive_template = "feeds/article_archive.html"
    
    latest_articles_template = "feeds/latest_articles.html"
    
    def render_page(self, request, template_name, context, page, **kwargs):
        """Renders this feed to the response."""
        opts = self.article_model._meta
        defaults = {"article_type": opts.verbose_name,
                    "article_type_plural": opts.verbose_name_plural}
        context.update(defaults)
        return super(FeedBase, self).render_page(request, template_name, context, page, **kwargs)
    
    def get_feed_url(self):
        """Returns the URL of the RSS feed for this page."""
        return reverse("feeds", kwargs={"url": ARTICLE_FEED_KEY}) + unicode(self.page.permalink or self.page.id) + u"/"
    
    feed_url = property(get_feed_url,
                        doc="The URL of the RSS feed for this page.")
    
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
        date = datetime.date(year, 1, 1)
        context = {"articles": articles,
                   "date": date,
                   "year": year}
        return self.render_to_response(request, self.year_archive_template, context)
    
    @content.view(r"^(\d{4})/(\d{1,2})/$")
    def month_archive(self, request, year, month):
        """Generates a page showing the articles in a given year."""
        year = int(year)
        month = int(month)
        all_articles = self.articles.filter(**{"%s__year" % self.date_field: year,
                                               "%s__month" % self.date_field: month})
        articles = self.get_page(request, all_articles)
        date = datetime.date(year, month, 1)
        context = {"articles": articles,
                   "date": date,
                   "year": year,
                   "month": month}
        return self.render_to_response(request, self.month_archive_template, context)
    
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
        context = {"year": getattr(article, self.date_field).year,
                   "month": getattr(article, self.date_field).month,
                   "article": article}
        return self.render_to_response(request, self.article_detail_template, context)


ARTICLE_FEED_KEY = "latest"


class ArticleFeed(Feed):
    
    """A feed of articles."""
    
    description_template = "feeds/article_description.html"
    
    def get_object(self, bits):
        """Allows customization of the feed."""
        if len(bits) == 1:
            return Page.objects.get_page(bits[0])
        raise Page.DoesNotExist, "No page id was specified."
        
    def title(self, obj=None):
        """Generates the feed title."""
        homepage = obj.homepage
        context = {"title": obj.browser_title or obj.title,
                   "site_title": homepage.browser_title or homepage.title}
        return template.loader.render_to_string("title.html", context)

    def link(self, obj):
        return obj.url

    def description(self, obj):
        """Generates the feed description."""
        return obj.meta_description
        
    def items(self, obj):
        """Generates the feed items."""
        content = obj.content
        articles = content.articles.order_by("-%s" % content.date_field, "-pk")
        return articles[:content.feed_length]


registered_feeds[ARTICLE_FEED_KEY] = ArticleFeed

