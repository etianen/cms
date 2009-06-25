"""Content types used by the news application."""


from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator, EmptyPage
from django.http import Http404
from django.utils.dates import MONTHS

from cms.apps.pages import content


class NewsFeed(content.Content):
    
    """An archive of published news articles."""
    
    icon = settings.CMS_MEDIA_URL + "img/content-types/news-feed.png"
    
    articles_per_page = content.PositiveIntegerField(required=True,
                                                     default=10)
    
    def get_published_articles(self):
        """Returns all the published articles for this news feed."""
        return self.page.article_set.order_by("is_featured", "-publication_date")
    
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
        all_articles = self.published_articles
        articles = self.get_page(request, all_articles)
        context = {"articles": articles}
        return self.render_to_response(request, "news/article_list.html", context)
    
    @content.view(r"^(\d+)/$")
    def year_archive(self, request, year):
        """Generates a page showing the articles in a given year."""
        year = int(year)
        all_articles = self.published_articles.filter(publication_date__year=year)
        articles = self.get_page(request, all_articles)
        context = {"articles": articles,
                   "title": "Archive for %i" % year,
                   "short_title": year,
                   "breadcrumbs": self.breadcrumbs,
                   "year": year}
        return self.render_to_response(request, "news/article_list.html", context)
    
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
                   "year": year}
        return self.render_to_response(request, "news/article_list.html", context)
    
    @content.view(r"^(\d+)/(\d+)/([a-zA-Z0-9_\-]+)/$")
    def article_detail(self, request, year, month, article_slug):
        """Dispatches to the article detail page."""
        year = int(year)
        month = int(month)
        all_articles = self.page.article_set.all().filter(publication_date__year=year,
                                                          publication_date__month=month)
        try:
            article = all_articles.get(url_title=article_slug)
        except ObjectDoesNotExist:
            raise Http404, "An article with a URL title of '%s' does not exist." % article_slug
        breadcrumbs = self.breadcrumbs + [{"url": self.reverse("year_archive", year), "title": year},
                                          {"url": self.reverse("month_archive", year, month), "title": MONTHS[month]},]
        context = {"breadcrumbs": breadcrumbs}
        return self.render_page(article, request, "news/article_detail.html", context)    
    
    