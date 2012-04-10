"""Models used by the CMS news app."""

from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models

import historylinks

from cms import sitemaps
from cms.apps.media.models import ImageRefField
from cms.apps.pages.models import ContentBase, Page
from cms.models import PageBase, OnlineBaseManager, HtmlField


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
    
    
def get_default_news_feed():
    """Returns the default news feed for the site."""
    try:
        return NewsFeed.objects.order_by("page__left")[0]
    except IndexError:
        return None


class Category(PageBase):
    
    """A category for news articles."""
    
    content_primary = HtmlField(
        "primary content",
        blank = True
    )
    
    def get_permalinks(self):
        """Returns a dictionary of all permalinks for the given category."""
        pages = Page.objects.filter(
            id__in = Article.objects.filter(
                categories = self
            ).values_list("news_feed_id", flat=True)
        )
        return dict(
            (u"page_{id}".format(id=page.id), page.reverse("article_category_archive", kwargs={
                "url_title": self.url_title,
            }))
            for page in pages
        )
    
    class Meta:
        verbose_name_plural = "categories"
        unique_together = (("url_title",),)
        ordering = ("title",)
        

class CategoryHistoryLinkAdapter(historylinks.HistoryLinkAdapter):
    
    """History link adapter for category models."""
    
    def get_permalinks(self, obj):
        """Returns all permalinks for the given category."""
        return obj.get_permalinks()

        
historylinks.register(Category, CategoryHistoryLinkAdapter)


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
    
    def get_absolute_url(self):
        """Returns the URL of the article."""
        return self.news_feed.page.reverse("article_detail", kwargs={
            "year": self.date.year,
            "month": self.date.strftime("%b").lower(),
            "day": self.date.day,
            "url_title": self.url_title,
        })
    
    class Meta:
        unique_together = (("news_feed", "date", "url_title",),)
        ordering = ("-date",)
        
        
historylinks.register(Article)


sitemaps.register(Article)