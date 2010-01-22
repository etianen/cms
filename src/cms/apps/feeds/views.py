"""Views used by the news application."""


import datetime

from django import template
from django.http import Http404, HttpResponse
from django.core import paginator
from django.conf import settings
from django.db.models import Q
from django.utils.feedgenerator import DefaultFeed

from cms.apps.pages.templatetags.pages import html


class FeedHelper(object):
    
    """Helper for generating item feeds."""
    
    def __init__(self, request, page_number=None, queryset=None, page_field=None, publication_date_field=None, expiry_date_field=None, num_articles_field=None, template_object_name=None, template_name=None):
        """Initializes the FeedHelper."""
        # Introspect the page details.
        self.request = request
        self.page = request.page
        self.content = self.page.content
        # Generate the querysets.
        self.page_field = page_field or "feed"
        self.queryset = queryset.filter(**{self.page_field: self.page})
        self.all_articles = self.queryset.all()
        # Introspect the model.
        self.model = self.queryset.model
        self.model_name = self.model.__name__.lower()
        # Flesh out the arguments.
        self.page_number = page_number
        self.num_articles_field = num_articles_field or "%ss_per_page" % self.model_name
        self.publication_date_field = publication_date_field or "publication_date"
        self.expiry_date_field = expiry_date_field or "expiry_date"
        self.template_object_name = template_object_name or "%s_list" % self.model_name
        self.dates = self.queryset.dates(self.publication_date_field, "month")
        self.template_name = template_name
        
    def filter(self, *args, **kwargs):
        """Filters the articles to display."""
        self.all_articles = self.all_articles.filter(*args, **kwargs)
        
    def render(self, default_template_name, extra_context, allow_empty_first_page=False):
        """Renders the feed."""
        # Paginate the articles.
        try:
            articles = paginator.Paginator(self.all_articles, getattr(self.content, self.num_articles_field), allow_empty_first_page=allow_empty_first_page).page(self.page_number)
        except paginator.InvalidPage:
            raise Http404, u"There are no %s to display" % self.model._meta.verbose_name_plural
        # Generate the context.
        template_object_name = self.template_object_name
        context = {template_object_name: articles,
                   "dates": self.dates}
        context.update(extra_context)
        # Render the template.
        template_name = self.template_name or default_template_name % (self.model._meta.app_label, self.model_name)
        return self.page.render_to_response(self.request, template_name, context)


def upcoming_index(request, page_number="1", **kwargs):
    """Generates a page of the upcoming events."""
    feed_helper = FeedHelper(request, page_number, **kwargs)
    # Filter the articles.
    now = datetime.datetime.now()
    feed_helper.filter(Q(**{"%s__gte" % feed_helper.publication_date_field: now}) | Q(**{"%s__gte" % feed_helper.expiry_date_field: now}))
    # Render the articles.
    context = {"date": now,}
    return feed_helper.render("%s/%s_upcoming.html", context, True)


def archive_index(request, page_number="1", **kwargs):
    """Generates a page of the latest articles."""
    feed_helper = FeedHelper(request, page_number, **kwargs)
    # Filter the articles.
    now = datetime.datetime.now()
    feed_helper.filter()
    # Render the articles.
    context = {"date": now,}
    return feed_helper.render("%s/%s_archive.html", context, True)
    

def archive_year(request, year, page_number="1", **kwargs):
    """Generates a page showing the articles in a given year."""
    year = int(year)
    feed_helper = FeedHelper(request, page_number, **kwargs)
    # Filter the articles.
    feed_helper.filter(**{"%s__year" % feed_helper.publication_date_field: year})
    # Render the articles.
    context = {"date": datetime.date(year, 1, 1),}
    return feed_helper.render("%s/%s_archive_year.html", context, True)


def archive_month(request, year, month, page_number="1", **kwargs):
    """Generates a page showing the articles in a given year."""
    year = int(year)
    month = int(month)
    feed_helper = FeedHelper(request, page_number, **kwargs)
    # Filter the articles.
    feed_helper.filter(**{"%s__year" % feed_helper.publication_date_field: year,
                          "%s__month" % feed_helper.publication_date_field: month})
    # Render the articles.
    context = {"date": datetime.date(year, 1, 1),}
    return feed_helper.render("%s/%s_archive_month.html", context, True)


def object_detail(request, year, month, article_slug, template_object_name=None, **kwargs):
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


def rss(request, **kwargs):
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
    
    