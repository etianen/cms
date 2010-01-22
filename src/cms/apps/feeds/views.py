"""Views used by the feeds application."""


import datetime

from django import template
from django.http import Http404, HttpResponse
from django.core import paginator
from django.conf import settings
from django.utils.feedgenerator import DefaultFeed

from cms.apps.pages.templatetags.pages import html


def index(request, page_number="1"):
    """Generates a page of the latest articles."""
    page_number = int(page_number)
    # Get the model information.
    page = request.page
    content = page.content
    article_model = content.article_model
    # Get the list of articles.
    all_articles = content.get_latest_articles()
    try:
        articles = paginator.Paginator(all_articles, content.articles_per_page)
    except paginator.InvalidPage:
        raise Http404, "There are no articles to display"
    # Generate the context.
    context = {"articles": articles,
               "date": datetime.datetime.now()}
    # Render the template.
    template_names = ("%s/index.html" % article_model._meta.app_label,
                      "feeds/index.html")
    return page.render_to_response(request, template_names, context)
    

def year_archive(request, year, page_number="1"):
    """Generates a page showing the articles in a given year."""
    page_number = int(page_number)
    year = int(year)
    # Get the model information.
    page = request.page
    content = page.content
    article_model = content.article_model
    # Get the list of articles.
    all_articles = content.get_articles().filter(**{"%s__year" % content.publication_date_field: year})
    try:
        articles = paginator.Paginator(all_articles, content.articles_per_page, allow_empty_first_page=False)
    except paginator.InvalidPage:
        raise Http404, "There are no articles to display"
    # Generate the context.
    context = {"articles": articles,
               "date": datetime.datetime(year, 1, 1)}
    # Render the template.
    template_names = ("%s/year_archive.html" % article_model._meta.app_label,
                      "feeds/year_archive.html")
    return page.render_to_response(request, template_names, context)


def month_archive(request, year, month, page_number="1"):
    """Generates a page showing the articles in a given month."""
    page_number = int(page_number)
    year = int(year)
    month = int(month)
    # Get the model information.
    page = request.page
    content = page.content
    article_model = content.article_model
    # Get the list of articles.
    all_articles = content.get_articles().filter(**{"%s__year" % content.publication_date_field: year,
                                                    "%s__month" % content.publication_date_field: month})
    try:
        articles = paginator.Paginator(all_articles, content.articles_per_page, allow_empty_first_page=False)
    except paginator.InvalidPage:
        raise Http404, "There are no articles to display"
    # Generate the context.
    context = {"articles": articles,
               "date": datetime.datetime(year, 1, 1)}
    # Render the template.
    template_names = ("%s/month_archive.html" % article_model._meta.app_label,
                      "feeds/month_archive.html")
    return page.render_to_response(request, template_names, context)


def article_detail(request, year, month, article_slug):
    """Dispatches to the article detail page."""
    year = int(year)
    month = int(month)
    # Get the model information.
    page = request.page
    content = page.content
    article_model = content.article_model
    # Get the article.
    try:
        article = content.get_articles().get(**{"%s__year" % content.publication_date_field: year,
                                                "%s__month" % content.publication_date_field: month,
                                                "url_title": article_slug})
    except article_model.DoesNotExist:
        raise Http404, "That article does not exist"
    # Generate the context.
    context = {"article": article,
               "date": getattr(article, content.publication_date_field)}
    # Render the template.
    template_names = ("%s/article_detail.html" % article_model._meta.app_label,
                      "feeds/article_detail.html")
    return article.render_to_response(request, template_names, context)


def rss(request):
    """Generates the RSS feed for this news feed."""
    # Get the model information.
    page = request.page
    content = page.content
    fullpath = "http://%s%%s" % page.site.domain 
    homepage = page.homepage
    # Generate the feed title.
    title_context = {"title": page.browser_title or page.title,
                     "site_title": homepage.browser_title or homepage.title}
    title = template.loader.render_to_string("title.html", title_context, template.RequestContext(request))
    # Get the list of articles.
    all_articles = content.get_articles().order_by("-%s" % content.publication_date_field)
    # Generate the head.
    feed = DefaultFeed(title=title,
                       link=fullpath % page.get_absolute_url(),
                       description=page.meta_description or homepage.meta_description,
                       language=settings.LANGUAGE_CODE)
    # Generate the feed body.
    for article in all_articles[:30]:
        feed.add_item(title=article.title,
                      link=fullpath % article.get_absolute_url(),
                      description=html(article.summary or article.content))
    # Generate the response.
    response = HttpResponse(mimetype=feed.mime_type)
    feed.write(response, settings.DEFAULT_CHARSET) 
    return response
    
    