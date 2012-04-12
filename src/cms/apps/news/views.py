"""Views used by the CMS news app."""

from django.views import generic
from django.shortcuts import get_object_or_404

from cms.views import PageDetailMixin
from cms.apps.news.models import Article, Category


class ArticleListMixin(object):
    
    """Base class for every view that handles articles."""
    
    model = Article
    
    make_object_list = True
    
    date_field = "date"
    
    allow_future = True  # The publication manager will take care of this.
    
    context_object_name = "article_list"
    
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
        )


class ArticleArchiveView(ArticleListMixin, generic.ArchiveIndexView):
    
    pass


class ArticleYearArchiveView(ArticleListMixin, generic.YearArchiveView):
    
    pass


class ArticleMonthArchiveView(ArticleListMixin, generic.MonthArchiveView):
    
    pass


class ArticleDateListMixin(object):
    
    """Adds in a date list for the current articles."""
    
    def get_context_data(self, **kwargs):
        """Adds in the context data for the article date list."""
        context = super(ArticleDateListMixin, self).get_context_data(**kwargs)
        context["date_list"] = self.get_queryset().dates("date", "month")
        return context


class ArticleDayArchiveView(ArticleDateListMixin, ArticleListMixin, generic.DayArchiveView):
    
    pass


class ArticleDetailView(ArticleDateListMixin, ArticleListMixin, PageDetailMixin, generic.DateDetailView):
    
    context_object_name = "article"


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