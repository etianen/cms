"""Views used by the feeds application."""


from django.http import Http404
from django.core import paginator


def index(request, page_number="1"):
    """Generates a page of the latest news articles."""
    page = request.page
    content = page.content
    # Paginate the articles.
    try:
        articles = paginator.Paginator(page.article_set.all(), content.articles_per_page).page(page_number)
    except paginator.InvalidPage:
        raise Http404, "There are no articles to display."
    # Render the template.
    context = {"articles": articles}
    return page.render_to_response(request, "news/index.html", context)


def year_archive(request, year, page_number="1"):
    """Generates a page showing the articles in a given year."""
    page = request.page
    content = page.content
    year = int(year)
    all_articles = content.articles.filter(**{"%s__year" % content.date_field: year})
    articles = content.get_page(request, all_articles)
    date = datetime.date(year, 1, 1)
    context = {"articles": articles,
               "date": date,
               "year": year}
    return page.render_to_response(request, content.year_archive_template, context)


def month_archive(request, year, month, page_number="1"):
    """Generates a page showing the articles in a given year."""
    page = request.page
    content = page.content
    year = int(year)
    month = int(month)
    all_articles = content.articles.filter(**{"%s__year" % content.date_field: year,
                                           "%s__month" % content.date_field: month})
    articles = content.get_page(request, all_articles)
    date = datetime.date(year, month, 1)
    context = {"articles": articles,
               "date": date,
               "year": year,
               "month": month}
    return page.render_to_response(request, content.month_archive_template, context)


def article_detail(request, year, month, article_slug):
    """Dispatches to the article detail page."""
    page = request.page
    content = page.content
    year = int(year)
    month = int(month)
    all_articles = content.article_model.objects.filter(**{"feed": content.page,
                                                        "%s__year" % content.date_field: year,
                                                        "%s__month" % content.date_field: month})
    try:
        article = all_articles.get(url_title=article_slug)
    except content.article_model.DoesNotExist:
        raise Http404, "An article with a URL title of '%s' does not exist." % article_slug
    context = {"year": getattr(article, content.date_field).year,
               "month": getattr(article, content.date_field).month,
               "article": article}
    return article.render_to_response(request, content.article_detail_template, context)

