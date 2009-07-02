"""Template tags used to render news articles."""


from django import template
from django.utils.dates import MONTHS

from cms.apps.news.models import Article
from cms.apps.pages.templatetags import Library 


register = Library()


@register.inclusion_tag("news/latest_news.html")
def latest_news(count=5):
    """Renders a list of the latest news articles."""
    articles = Article.published_objects.all()[:count]
    context = {"articles": articles}
    return context


@register.context_tag
def news_archive(context, page, year):
    """Renders the news archive for the given page."""
    page_content = page.content
    request = context["request"]
    available_months = page_content.published_articles.dates("publication_date", "month")
    # Generate the news archive.
    news_archive = []
    year = None
    for date in available_months:
        month = date.month
        if date.year != year:
            year = date.year
            news_archive.append({"year": year, "months": [], "url": page_content.reverse("year_archive", year)})
        news_archive[-1]["months"].append({"month": MONTHS[month], "url": page_content.reverse("month_archive", year, month)})
    # Generate the context.
    context = {"request": request,
               "page": page,
               "year": year,
               "news_archive": news_archive}
    return template.loader.render_to_string("news/news_archive.html", context)

