"""Views used by the news application."""


import datetime

from django import template
from django.http import Http404, HttpResponse
from django.core import paginator
from django.conf import settings
from django.db.models import Q
from django.utils.feedgenerator import DefaultFeed

from cms.apps.pages.templatetags.pages import html


PAGE_FIELD = "feed"
PUBLICATION_DATE_FIELD = "publication_date"
EXPIRY_DATE_FIELD = "expiry_date"


def upcoming_index(request, page_number="1", queryset=None, page_field=PAGE_FIELD, publication_date_field=PUBLICATION_DATE_FIELD, expiry_date_field=EXPIRY_DATE_FIELD, num_articles_field=None, template_object_name=None, template_name=None):
    """Generates a page of the upcoming events."""
    page = request.page
    content = page.content
    article_set = queryset.filter(**{PAGE_FIELD: page})
    model = article_set.model
    model_name = model.__name__.lower()
    num_articles_field = num_articles_field or "%ss_per_page" % model_name
    # Paginate the events.
    now = datetime.datetime.now()
    all_articles = article_set.filter(Q(**{"%s__gte" % publication_date_field: now}) | Q(**{"%s__gte" % expiry_date_field: now}))
    try:
        articles = paginator.Paginator(all_articles, getattr(content, num_articles_field), allow_empty_first_page=True).page(page_number)
    except paginator.InvalidPage:
        raise Http404, u"There are no events to display"
    # Render the template.
    date = datetime.datetime.now()
    dates = article_set.dates("start_date", "month")
    template_object_name = template_object_name or "%s_list" % model_name
    context = {template_object_name: articles,
               "date": date,
               "dates": dates}
    template_name = template_name or "%s/%s_upcoming.html" % (model._meta.app_label, model_name)
    return page.render_to_response(request, template_name, context)


def archive_index(request, page_number="1", queryset=None, page_field=PAGE_FIELD, publication_date_field=PUBLICATION_DATE_FIELD, expiry_date_field=EXPIRY_DATE_FIELD, num_articles_field=None, template_object_name=None, template_name=None):
    """Generates a page of the latest articles."""
    page = request.page
    content = page.content
    article_set = queryset.filter(**{PAGE_FIELD: page})
    model = article_set.model
    model_name = model.__name__.lower()
    num_articles_field = num_articles_field or "%ss_per_page" % model_name
    # Paginate the articles.
    all_articles = article_set.all()
    try:
        articles = paginator.Paginator(all_articles, getattr(content, num_articles_field), allow_empty_first_page=True).page(page_number)
    except paginator.InvalidPage:
        raise Http404, u"There are no %s to display" % model._meta.verbose_name_plural
    # Render the template.
    date = datetime.datetime.now()
    dates = article_set.dates(publication_date_field, "month")
    template_object_name = template_object_name or "%s_list" % model_name
    context = {template_object_name: articles,
               "date": date,
               "dates": dates}
    template_name = template_name or "%s/%s_archive.html" % (model._meta.app_label, model_name)
    return page.render_to_response(request, template_name, context)


def archive_year(request, year, page_number="1", queryset=None, page_field=PAGE_FIELD, publication_date_field=PUBLICATION_DATE_FIELD, expiry_date_field=EXPIRY_DATE_FIELD, num_articles_field=None, template_object_name=None, template_name=None):
    """Generates a page showing the articles in a given year."""
    page = request.page
    content = page.content
    article_set = queryset.filter(**{PAGE_FIELD: page})
    model = article_set.model
    model_name = model.__name__.lower()
    num_articles_field = num_articles_field or "%ss_per_page" % model_name
    year = int(year)
    # Paginate the articles.
    all_articles = article_set.filter(**{"%s__year" % publication_date_field: year})
    try:
        articles = paginator.Paginator(all_articles, getattr(content, num_articles_field), allow_empty_first_page=False).page(page_number)
    except paginator.InvalidPage:
        raise Http404, u"There are no %s to display" % model._meta.verbose_name_plural
    # Render the template.
    date = datetime.date(year, 1, 1)
    dates = article_set.dates(publication_date_field, "month")
    template_object_name = template_object_name or "%s_list" % model_name
    context = {template_object_name: articles,
               "date": date,
               "dates": dates}
    template_name = template_name or "%s/%s_archive_year.html" % (model._meta.app_label, model_name)
    return page.render_to_response(request, template_name, context)


def archive_month(request, year, month, page_number="1", queryset=None, page_field=PAGE_FIELD, publication_date_field=PUBLICATION_DATE_FIELD, expiry_date_field=EXPIRY_DATE_FIELD, num_articles_field=None, template_object_name=None, template_name=None):
    """Generates a page showing the articles in a given year."""
    page = request.page
    content = page.content
    article_set = queryset.filter(**{PAGE_FIELD: page})
    model = article_set.model
    model_name = model.__name__.lower()
    num_articles_field = num_articles_field or "%ss_per_page" % model_name
    year = int(year)
    month = int(month)
    # Paginate the articles.
    all_articles = article_set.filter(**{"%s__year" % publication_date_field: year,
                                         "%s__month" % publication_date_field: month})
    try:
        articles = paginator.Paginator(all_articles, getattr(content, num_articles_field), allow_empty_first_page=False).page(page_number)
    except paginator.InvalidPage:
        raise Http404, u"There are no %s to display" % model._meta.verbose_name_plural
    # Render the template.
    date = datetime.date(year, month, 1)
    dates = article_set.dates(publication_date_field, "month")
    template_object_name = template_object_name or "%s_list" % model_name
    context = {template_object_name: articles,
               "date": date,
               "dates": dates}
    template_name = template_name or "%s/%s_archive_month.html" % (model._meta.app_label, model_name)
    return page.render_to_response(request, template_name, context)


def object_detail(request, year, month, article_slug, page_number="1", queryset=None, page_field=PAGE_FIELD, publication_date_field=PUBLICATION_DATE_FIELD, expiry_date_field=EXPIRY_DATE_FIELD, num_articles_field=None, template_object_name=None, template_name=None):
    """Dispatches to the article detail page."""
    page = request.page
    article_set = queryset.filter(**{PAGE_FIELD: page})
    model = article_set.model
    model_name = model.__name__.lower()
    month = int(month)
    # Get the article.
    try:
        article = article_set.get(**{"%s__year" % publication_date_field: year,
                                     "%s__month" % publication_date_field: month,
                                     "url_title": article_slug})
    except model.DoesNotExist:
        raise Http404, u"That %s does not exist" % model_name
    # Render the template.
    dates = article_set.dates(publication_date_field, "month")
    template_object_name = template_object_name or model_name
    context = {template_object_name: article,
               "date": getattr(article, publication_date_field),
               "dates": dates}
    template_name = template_name or "%s/%s_detail.html" % (model._meta.app_label, model_name)
    return article.render_to_response(request, template_name, context)


def rss(request, queryset=None, page_field=PAGE_FIELD, publication_date_field=PUBLICATION_DATE_FIELD, expiry_date_field=EXPIRY_DATE_FIELD, num_articles_field=None, template_object_name=None, template_name=None):
    """Generates the RSS feed for this news feed."""
    page = request.page
    article_set = queryset.filter(**{PAGE_FIELD: page}).order_by("-" + publication_date_field)
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
    for article in article_set.all()[:30]:
        feed.add_item(title=article.title,
                      link=fullpath % article.get_absolute_url(),
                      description=html(article.summary or article.content))
    # Generate the response.
    response = HttpResponse(mimetype=feed.mime_type)
    feed.write(response, settings.DEFAULT_CHARSET) 
    return response
    
    