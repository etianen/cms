"""Views used by the feeds application."""


import datetime

from django.http import Http404, HttpResponse
from django.conf import settings
from django.utils.feedgenerator import DefaultFeed
from django.shortcuts import render_to_response
from django.template import RequestContext

from cms.core import html


def index(request):
    """Generates a page of the latest articles."""
    # Get the model information.
    page = request.page
    content = page.content
    article_model = content.article_model
    # Get the list of articles.
    articles = content.get_latest_articles()
    # Generate the context.
    context = {"articles": articles,
               "date": datetime.datetime.now()}
    # Render the template.
    template_names = ("%s/index.html" % article_model._meta.app_label,
                      "feeds/index.html")
    return render_to_response(template_names, context, RequestContext(request))
    

def year_archive(request, year):
    """Generates a page showing the articles in a given year."""
    year = int(year)
    # Get the model information.
    page = request.page
    content = page.content
    article_model = content.article_model
    # Get the list of articles.
    articles = content.get_articles().filter(**{"%s__year" % article_model.date_field_name: year})
    if articles.count() == 0:
        raise Http404, "There are no articles to display."
    # Generate the context.
    context = {"articles": articles,
               "date": datetime.datetime(year, 1, 1)}
    # Render the template.
    template_names = ("%s/year_archive.html" % article_model._meta.app_label,
                      "feeds/year_archive.html")
    return render_to_response(template_names, context, RequestContext(request))


def month_archive(request, year, month):
    """Generates a page showing the articles in a given month."""
    year = int(year)
    month = int(month)
    # Get the model information.
    page = request.page
    content = page.content
    article_model = content.article_model
    # Get the list of articles.
    articles = content.get_articles().filter(**{"%s__year" % article_model.date_field_name: year,
                                                "%s__month" % article_model.date_field_name: month})
    if articles.count() == 0:
        raise Http404, "There are no articles to display."
    # Generate the context.
    context = {"articles": articles,
               "date": datetime.datetime(year, month, 1)}
    # Render the template.
    template_names = ("%s/month_archive.html" % article_model._meta.app_label,
                      "feeds/month_archive.html")
    return render_to_response(template_names, context, RequestContext(request))


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
        article = content.get_articles().get(**{"%s__year" % article_model.date_field_name: year,
                                                "%s__month" % article_model.date_field_name: month,
                                                "url_title": article_slug})
    except article_model.DoesNotExist:
        raise Http404, "That article does not exist"
    # Generate the context.
    context = {"article": article,
               "date": getattr(article, article_model.date_field_name)}
    # Render the template.
    template_names = ("%s/article_detail.html" % article_model._meta.app_label,
                      "feeds/article_detail.html")
    return article.render_to_response(request, template_names, context)


def rss(request):
    """Generates the RSS feed for this news feed."""
    # Get the model information.
    page = request.page
    content = page.content
    article_model = content.article_model
    fullpath = "http://%s%%s" % page.site.domain 
    homepage = page.homepage
    # Generate the feed title.
    page_title = page.browser_title or page.title
    site_title = homepage.browser_title or homepage.title
    title = "%s - %s" % (page_title, site_title)
    # Get the list of articles.
    all_articles = content.get_articles().order_by("-%s" % article_model.date_field_name)
    # Generate the head.
    feed = DefaultFeed(title=title,
                       link=fullpath % page.get_absolute_url(),
                       description=page.meta_description or homepage.meta_description,
                       language=settings.LANGUAGE_CODE)
    # Generate the feed body.
    for article in all_articles[:30]:
        feed.add_item(title=article.title,
                      link=fullpath % article.get_absolute_url(),
                      description=html.process(article.summary or article.content))
    # Generate the response.
    response = HttpResponse(mimetype=feed.mime_type)
    feed.write(response, settings.DEFAULT_CHARSET) 
    return response
    
    