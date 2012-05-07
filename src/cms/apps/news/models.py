"""Models used by the CMS news app."""

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db import models

from cms import sitemaps, externals
from cms.apps.media.models import ImageRefField
from cms.apps.pages.models import ContentBase, Page
from cms.models import PageBase, OnlineBaseManager, HtmlField, PageBaseSearchAdapter


class NewsFeed(ContentBase):
    
    """A stream of news articles."""
    
    icon = "news/img/news-feed.png"

    # The heading that the admin places this content under.
    classifier = "syndication"

    # The urlconf used to power this content's views.
    urlconf = "cms.apps.news.urls"
    
    content_primary = HtmlField(
        "primary content",
        blank = True
    )
    
    per_page = models.IntegerField(
        "articles per page",
        default = 5,
        blank = True,
        null = True,
    )


def get_default_news_page():
    """Returns the default news page."""
    try:
        return Page.objects.filter(
            content_type = ContentType.objects.get_for_model(NewsFeed),
        ).order_by("left")[0]
    except IndexError:
        return None
    
    
def get_default_news_feed():
    """Returns the default news feed for the site."""
    page = get_default_news_page()
    if page:
        return page.content
    return None


class Category(PageBase):
    
    """A category for news articles."""
    
    content_primary = HtmlField(
        "primary content",
        blank = True
    )
    
    def _get_permalink_for_page(self, page):
        """Returns the URL for this category for the given page."""
        return page.reverse("article_category_archive", kwargs={
            "url_title": self.url_title,
        })
    
    def _get_permalinks(self):
        """Returns a dictionary of all permalinks for the given category."""
        pages = Page.objects.filter(
            id__in = Article.objects.filter(
                categories = self
            ).values_list("news_feed_id", flat=True)
        )
        return dict(
            (u"page_{id}".format(id=page.id), self._get_permalink_for_page(page))
            for page in pages
        )
    
    class Meta:
        verbose_name_plural = "categories"
        unique_together = (("url_title",),)
        ordering = ("title",)
        

class CategoryHistoryLinkAdapter(externals.historylinks.HistoryLinkAdapter):
    
    """History link adapter for category models."""
    
    def get_permalinks(self, obj):
        """Returns all permalinks for the given category."""
        return obj._get_permalinks()

        
externals.historylinks("register", Category, CategoryHistoryLinkAdapter)


class ArticleManager(OnlineBaseManager):
    
    """Manager for Article models."""
    
    def select_published(self, queryset):
        queryset = super(ArticleManager, self).select_published(queryset)
        queryset = queryset.filter(
            date__lte = timezone.now(),
        )
        return queryset


class Article(PageBase):
    
    """A news article."""
    
    objects = ArticleManager()
    
    news_feed = models.ForeignKey(
        NewsFeed,
        default = get_default_news_feed,
    )
    
    date = models.DateField(
        db_index = True,
        default = timezone.now,
    )
    
    image = ImageRefField(
        blank = True,
        null = True,
    )
    
    content = HtmlField(
        blank = True,
    )
    
    summary = HtmlField(
        blank = True,
    )
    
    categories = models.ManyToManyField(
        Category,
        blank = True,
    )
    
    authors = models.ManyToManyField(
        User,
        blank = True,
    )
    
    def _get_permalink_for_page(self, page):
        """Returns the URL of this article for the given news feed page."""
        return page.reverse("article_detail", kwargs={
            "year": self.date.year,
            "month": self.date.strftime("%b").lower(),
            "day": self.date.day,
            "url_title": self.url_title,
        })
    
    def get_absolute_url(self):
        """Returns the URL of the article."""
        return self._get_permalink_for_page(self.news_feed.page)
    
    class Meta:
        unique_together = (("news_feed", "date", "url_title",),)
        ordering = ("-date",)
        
        
externals.historylinks("register", Article)


sitemaps.register(Article)


externals.watson("register", Article, adapter_cls=PageBaseSearchAdapter)