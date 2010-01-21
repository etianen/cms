"""Views used by the feeds application."""


import datetime

from django.http import Http404
from django.core import paginator


def index(request, page_number="1"):
    """Generates a page of the latest news articles."""
    page = request.page
    content = page.content
    # Paginate the articles.
    all_articles = page.article_set.all()
    try:
        articles = paginator.Paginator(all_articles, content.articles_per_page).page(page_number)
    except paginator.InvalidPage:
        raise Http404, "There are no articles to display"
    # Render the template.
    date = datetime.datetime.now()
    context = {"articles": articles,
               "date": date}
    return page.render_to_response(request, "news/index.html", context)


def year_archive(request, year, page_number="1"):
    """Generates a page showing the articles in a given year."""
    page = request.page
    content = page.content
    year = int(year)
    # Paginate the articles.
    all_articles = page.article_set.filter(publication_date__year=year)
    try:
        articles = paginator.Paginator(all_articles, content.articles_per_page, allow_empty_first_page=False).page(page_number)
    except paginator.InvalidPage:
        raise Http404, "There are no articles to display."
    # Render the template.
    date = datetime.date(year, 1, 1)
    context = {"articles": articles,
               "date": date}
    return page.render_to_response(request, "news/year_archive.html", context)


def month_archive(request, year, month, page_number="1"):
    """Generates a page showing the articles in a given year."""
    page = request.page
    content = page.content
    year = int(year)
    month = int(month)
    # Paginate the articles.
    all_articles = page.article_set.filter(publication_date__year=year,
                                           publication_date__month=month)
    try:
        articles = paginator.Paginator(all_articles, content.articles_per_page, allow_empty_first_page=False).page(page_number)
    except paginator.InvalidPage:
        raise Http404, "There are no articles to display"
    # Render the template.
    date = datetime.date(year, month, 1)
    context = {"articles": articles,
               "date": date}
    return page.render_to_response(request, "news/month_archive.html", context)


def article_detail(request, year, month, article_slug):
    """Dispatches to the article detail page."""
    page = request.page
    year = int(year)
    month = int(month)
    # Get the article.
    try:
        article = page.article_set.get(publication_date__year=year,
                                       publication_date__month=month,
                                       url_title=article_slug)
    except page.article_set.model.DoesNotExist:
        raise Http404, "That article does not exist"
    # Render the template.
    context = {"article": article,
               "date": article.publication_date}
    return article.render_to_response(request, "news/article_detail.html", context)

