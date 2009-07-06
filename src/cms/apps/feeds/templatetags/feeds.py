"""Template tags used to render feed articles."""


from django import template
from django.utils.dates import MONTHS

from cms.apps.pages.models import Page
from cms.apps.pages.templatetags import Library 


register = Library()


@register.inclusion_tag("feeds/feed.html")
def feed(page):
    """Generates a link to the RSS feed for the page."""
    page = Page.objects.get_page(page)
    context = {"url": page.content.feed_url,
               "title": page.title}
    return context


@register.context_tag
def latest_articles(context, page, count=5):
    """Renders a list of the latest news articles."""
    try:
        page = Page.objects.get_page(page)
    except Page.DoesNotExist:
        return ""
    page_content = page.content
    articles = page_content.latest_articles.all()[:count]
    context = {"articles": articles,
               "page": page}
    return template.loader.render_to_string(page_content.latest_articles_template, context)


@register.filter
def date_field(article):
    """Returns the value of the date field in the article."""
    page_content = article.feed.content
    return getattr(article, page_content.date_field)


@register.context_tag
def article_archive(context, page, year):
    """Renders the news archive for the given page."""
    page_content = page.content
    request = context["request"]
    available_months = page_content.articles.dates(page_content.date_field, "month")
    # Generate the news archive.
    article_archive = []
    year = None
    for date in available_months:
        month = date.month
        if date.year != year:
            year = date.year
            article_archive.append({"year": year, "months": [], "url": page_content.reverse("year_archive", year)})
        article_archive[-1]["months"].append({"month": MONTHS[month], "url": page_content.reverse("month_archive", year, month)})
    # Generate the context.
    context = {"request": request,
               "page": page,
               "year": year,
               "article_archive": article_archive,
               "article_type_plural": page_content.article_model._meta.verbose_name_plural}
    return template.loader.render_to_string(page_content.article_archive_template, context)

