"""Views used by the news application."""


import datetime

from django import template
from django.http import Http404, HttpResponse
from django.core import paginator
from django.conf import settings
from django.utils.feedgenerator import DefaultFeed

from cms.apps.pages.templatetags.pages import html


ARTICLE_SET_ATTR = "article_set"
ARTICLES_PER_PAGE_ATTR = "articles_per_page"
ARTICLE_DATE_ATTR = "publication_date"
LIST_NAME = "articles"


def index(request, page_number="1", article_set_attr=ARTICLE_SET_ATTR, articles_per_page_attr=ARTICLES_PER_PAGE_ATTR, article_date_attr=ARTICLE_DATE_ATTR, list_name=LIST_NAME, template_name="news/index.html"):
    """Generates a page of the latest news articles."""
    page = request.page
    content = page.content
    article_set = getattr(page, article_set_attr)
    # Paginate the articles.
    all_articles = article_set.all()
    try:
        articles = paginator.Paginator(all_articles, getattr(content, articles_per_page_attr)).page(page_number)
    except paginator.InvalidPage:
        raise Http404, "There are no articles to display"
    # Render the template.
    date = datetime.datetime.now()
    dates = article_set.dates(article_date_attr, "month")
    context = {list_name: articles,
               "date": date,
               "dates": dates}
    return page.render_to_response(request, template_name, context)


def year_archive(request, year, page_number="1", article_set_attr=ARTICLE_SET_ATTR, articles_per_page_attr=ARTICLES_PER_PAGE_ATTR, article_date_attr=ARTICLE_DATE_ATTR, list_name=LIST_NAME, template_name="news/year_archive.html"):
    """Generates a page showing the articles in a given year."""
    page = request.page
    content = page.content
    article_set = getattr(page, article_set_attr)
    year = int(year)
    # Paginate the articles.
    all_articles = article_set.filter(**{"%s__year" % article_date_attr: year})
    try:
        articles = paginator.Paginator(all_articles, getattr(content, articles_per_page_attr), allow_empty_first_page=False).page(page_number)
    except paginator.InvalidPage:
        raise Http404, "There are no articles to display."
    # Render the template.
    date = datetime.date(year, 1, 1)
    dates = article_set.dates(article_date_attr, "month")
    context = {list_name: articles,
               "date": date,
               "dates": dates}
    return page.render_to_response(request, template_name, context)


def month_archive(request, year, month, page_number="1", article_set_attr=ARTICLE_SET_ATTR, articles_per_page_attr=ARTICLES_PER_PAGE_ATTR, article_date_attr=ARTICLE_DATE_ATTR, list_name=LIST_NAME, template_name="news/month_archive.html"):
    """Generates a page showing the articles in a given year."""
    page = request.page
    content = page.content
    article_set = getattr(page, article_set_attr)
    year = int(year)
    month = int(month)
    # Paginate the articles.
    all_articles = article_set.filter(**{"%s__year" % article_date_attr: year,
                                         "%s__month" % article_date_attr: month})
    try:
        articles = paginator.Paginator(all_articles, getattr(content, articles_per_page_attr), allow_empty_first_page=False).page(page_number)
    except paginator.InvalidPage:
        raise Http404, "There are no articles to display"
    # Render the template.
    date = datetime.date(year, month, 1)
    dates = article_set.dates(article_date_attr, "month")
    context = {list_name: articles,
               "date": date,
               "dates": dates}
    return page.render_to_response(request, template_name, context)


def article_detail(request, year, month, article_slug, article_set_attr=ARTICLE_SET_ATTR, article_date_attr=ARTICLE_DATE_ATTR, article_name="article", template_name="news/article_detail.html"):
    """Dispatches to the article detail page."""
    page = request.page
    year = int(year)
    article_set = getattr(page, article_set_attr)
    month = int(month)
    # Get the article.
    try:
        article = article_set.get(**{"%s__year" % article_date_attr: year,
                                     "%s__month" % article_date_attr: month,
                                     "url_title": article_slug})
    except article_set.model.DoesNotExist:
        raise Http404, "That article does not exist"
    # Render the template.
    dates = article_set.dates(article_date_attr, "month")
    context = {article_name: article,
               "date": getattr(article, article_date_attr),
               "dates": dates}
    return article.render_to_response(request, template_name, context)


def rss(request, article_set_attr=ARTICLE_SET_ATTR, article_date_attr=ARTICLE_DATE_ATTR):
    """Generates the RSS feed for this news feed."""
    page = request.page
    site = page.site
    fullpath = "http://%s%%s" % site.domain 
    homepage = page.homepage
    article_set = getattr(page, article_set_attr).order_by("-" + article_date_attr)
    # Generate the feed title.
    title_context = {"title": page.browser_title or page.title,
                     "site_title": homepage.browser_title or homepage.title}
    title = template.loader.render_to_string("title.html", title_context, template.RequestContext(request))
    # Generate the head.
    feed = DefaultFeed(title=title,
                       link=fullpath % page.get_absolute_url(),
                       description=page.meta_description or homepage.meta_description,
                       language=settings.LANGUAGE_CODE)
    # Generate the feed body.
    for article in article_set.all()[:30]:
        feed.add_item(title=article.title,
                      link=fullpath % article.get_absolute_url(),
                      description=html(article.summary or article.content))
    # Generate the response.
    response = HttpResponse(mimetype=feed.mime_type)
    feed.write(response, settings.DEFAULT_CHARSET) 
    return response
    
    