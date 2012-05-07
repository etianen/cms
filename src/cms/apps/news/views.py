"""Views used by the CMS news app."""

from django.views import generic
from django.views.generic.list import BaseListView
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import DefaultFeed
from django.http import HttpResponse

from cms.views import PageDetailMixin
from cms.apps.news.models import Article, Category
from cms.html import process as process_html


class ArticleListMixin(object):
    
    """Base class for every view that handles articles."""
    
    model = Article
    
    make_object_list = True
    
    date_field = "date"
    
    allow_future = True  # The publication manager will take care of this.
    
    context_object_name = "article_list"
    
    def get_paginate_by(self, queryset):
        """Returns the number of articles to show per page."""
        return self.request.pages.current.content.per_page
    
    def get_context_data(self, **kwargs):
        """Returns the context data for the view."""
        context = super(ArticleListMixin, self).get_context_data(**kwargs)
        category_list = Category.objects.filter(
            article__news_feed__page = self.request.pages.current,
        ).distinct()
        context["category_list"] = category_list
        return context
    
    def get_queryset(self):
        """Returns the article queryset."""
        return super(ArticleListMixin, self).get_queryset().prefetch_related(
            "categories",
            "authors",
        ).select_related("image").filter(
            news_feed__page = self.request.pages.current,
        ).order_by("-date")


class ArticleArchiveView(ArticleListMixin, generic.ArchiveIndexView):
    
    allow_empty = True


class ArticleFeedView(ArticleListMixin, BaseListView):
    
    """Generates an RSS feed of articles."""
    
    def get(self, request):
        """Generates the RSS feed."""
        page = request.pages.current
        # Write the feed headers.
        feed = DefaultFeed(
            title = page.title,
            link = page.get_absolute_url(),
            description = page.meta_description,
        )
        # Write the feed items.
        for article in self.get_queryset()[:30]:
            feed.add_item(
                title = article.title,
                link = article.get_absolute_url(),
                description = process_html(article.summary or article.content),
                pubdate = article.date,
            )
        # Write the response.
        content = feed.writeString("utf-8")
        response = HttpResponse(content)
        response["Content-Type"] = feed.mime_type
        response["Content-Length"] = len(content)
        return response


class ArticleYearArchiveView(ArticleListMixin, generic.YearArchiveView):
    
    pass


class ArticleMonthArchiveView(ArticleListMixin, generic.MonthArchiveView):
    
    pass


class ArticleDayArchiveView(ArticleListMixin, generic.DayArchiveView):
    
    pass


class ArticleDetailView(ArticleListMixin, PageDetailMixin, generic.DateDetailView):
    
    context_object_name = "article"
    
    def get_context_data(self, **kwargs):
        """Adds the next and previous articles to the context."""
        context = super(ArticleDetailView, self).get_context_data(**kwargs)
        # Get the next article.
        try:
            next_article = self.get_queryset().filter(
                date__lt = self.object.date,
            )[0]
        except IndexError:
            next_article = None
        context["next_article"] = next_article
        # Get the previous article.
        try:
            prev_article = self.get_queryset().reverse().filter(
                date__gt = self.object.date,
            )[0]
        except IndexError:
            prev_article = None
        context["prev_article"] = prev_article
        # All done!
        return context


class ArticleCategoryArchiveView(PageDetailMixin, ArticleArchiveView):
    
    """An archive view for articles by category."""
    
    template_name = "news/article_category_archive.html"
    
    def get_queryset(self):
        """Returns the queryset filtered by category."""
        return super(ArticleCategoryArchiveView, self).get_queryset().filter(
            categories = self.object,
        )
        
    def get_context_data(self, **kwargs):
        """Adds the category to the context."""
        context = super(ArticleCategoryArchiveView, self).get_context_data(**kwargs)
        context["category"] = self.object
        return context
    
    def dispatch(self, request, *args, **kwargs):
        """Parses the category from the request."""
        self.object = get_object_or_404(Category,
            url_title = kwargs["url_title"],
        )
        return super(ArticleCategoryArchiveView, self).dispatch(request, *args, **kwargs)