"""Base content classes for feed-based content."""


from django import template
from django.contrib.syndication.feeds import Feed
from django.conf import settings
from django.core.paginator import EmptyPage, Paginator
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
    
    urlconf = "cms.apps.feeds.urls"

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
    
    def get_page(self, request, models, items_per_page=None, pagination_key=None):
        """Returns an object paginator for the given models."""
        items_per_page = items_per_page or settings.ITEMS_PER_PAGE
        pagination_key = pagination_key or settings.PAGINATION_KEY
        page = request.GET.get(pagination_key, 1)
        try:
            page = int(page)
        except ValueError:
            raise Http404, "'%s' is not a valid page number." % page 
        paginator = Paginator(models, items_per_page)
        try:
            page = paginator.page(page)
        except EmptyPage:
            raise Http404, "There are no models on this page."
        return page
    
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

