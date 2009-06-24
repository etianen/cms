"""Content types used by the news application."""


from django.conf import settings
from django.core.paginator import Paginator, EmptyPage
from django.http import Http404

from cms.apps.pages import content


class NewsFeed(content.Content):
    
    """An archive of published news articles."""
    
    icon = settings.CMS_MEDIA_URL + "img/content-types/news-feed.png"
    
    articles_per_page = content.PositiveIntegerField(required=True,
                                                     default=10)
    
    def get_articles(self):
        """Returns all the published articles for this news feed."""
        return self.page.article_set.order_by("is_featured", "-publication_date")
    
    articles = property(get_articles,
                        doc="All the published articles for this news feed.")
    
    @content.view(r"^$")
    def index(self, request):
        """Generates a page of the latest news articles."""
        # Get the paginated articles.
        page = request.GET.get(settings.PAGINATION_KEY, 1)
        try:
            page = int(page)
        except ValueError:
            raise Http404, "'%s' is not a valid page number." % page 
        all_articles = self.articles
        paginator = Paginator(all_articles, self.articles_per_page)
        try:
            articles = paginator.page(page)
        except EmptyPage:
            raise Http404, "There are no articles on this page."
        # Generate the context.
        context = {"articles": articles}
        # Render the template.
        return self.render_to_response(request, "news/latest.html", context)
    

class NewsArticle(content.Content):
    
    """A published news article."""
    
    summary = content.TextField(help_text="A short summary of this article.  This will be used on news pages and RSS feeds.  If not specified, then a summarized version of the content will be used.")
    
    