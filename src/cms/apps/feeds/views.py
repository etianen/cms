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
    all_articles = content.get_latest()
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


def article_detail(request, year, month, article_slug, template_object_name=None):
    """Dispatches to the article detail page."""
    feed_helper = FeedHelper(request, **kwargs)
    # Get the article.
    try:
        article = feed_helper.all_articles.get(**{"%s__year" % feed_helper.publication_date_field: year,
                                                  "%s__month" % feed_helper.publication_date_field: month,
                                                  "url_title": article_slug})
    except feed_helper.model.DoesNotExist:
        raise Http404, u"That %s does not exist" % feed_helper.model_name
    # Render the template.
    template_object_name = template_object_name or feed_helper.model_name
    context = {template_object_name: article,
               "date": getattr(article, feed_helper.publication_date_field),
               "dates": feed_helper.dates}
    template_name = feed_helper.template_name or "%s/%s_detail.html" % (feed_helper.model._meta.app_label, feed_helper.model_name)
    return article.render_to_response(request, template_name, context)


def rss(request):
    """Generates the RSS feed for this news feed."""
    feed_helper = FeedHelper(request, **kwargs)
    all_articles = feed_helper.all_articles.order_by("-" + feed_helper.publication_date_field)
    page = feed_helper.page
    fullpath = "http://%s%%s" % page.site.domain 
    homepage = page.homepage
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
    for article in all_articles[:30]:
        feed.add_item(title=article.title,
                      link=fullpath % article.get_absolute_url(),
                      description=html(article.summary or article.content))
    # Generate the response.
    response = HttpResponse(mimetype=feed.mime_type)
    feed.write(response, settings.DEFAULT_CHARSET) 
    return response
    
    