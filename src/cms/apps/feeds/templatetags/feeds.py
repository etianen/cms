"""Template tags used to render feed articles."""


import urllib2, datetime
from xml.dom import minidom

from django import template
from django.core.cache import cache
from django.core.serializers.xml_serializer import getInnerText
from django.utils.dates import MONTHS
from django.utils import simplejson

from cms.apps.pages.models import Page
from cms.apps.pages.templatetags import Library


register = Library()


@register.inclusion_tag("feeds/feed_link.html")
def feed_link(page):
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
    context.push()
    try:
        context.update({"page": page,
                        "year": year,
                        "article_archive": article_archive})
        return template.loader.render_to_string(page_content.article_archive_template, context)
    finally:
        context.pop()
    

@register.inclusion_tag("feeds/rss_feed.html")
def rss_feed(url, count=5):
    """Generice feed mirroring tag."""
    cache_key = "feeds.rss_feed:%s" % url
    feed = cache.get(cache_key)
    if feed is None:
        try:
            response = urllib2.urlopen(url)
        except urllib2.URLError:
            feed = {}
        else:
            result = minidom.parse(response)
            items = [{"title": getInnerText(item.getElementsByTagName("title")[0]),
                      "url": getInnerText(item.getElementsByTagName("link")[0]),
                      "date": datetime.datetime.strptime(getInnerText(item.getElementsByTagName("pubDate")[0]), "%a, %d %b %Y %H:%M:%S +0000"),
                      "summary": getInnerText(item.getElementsByTagName("description")[0]),} for item in result.getElementsByTagName("item")]
            feed = {"items": items,
                    "title": getInnerText(result.getElementsByTagName("title")[0]),
                    "url": getInnerText(result.getElementsByTagName("link")[0])}
        cache.set(cache_key, feed)
    context = {"feed": feed}
    return context


@register.inclusion_tag("feeds/twitter_feed.html")
def twitter_feed(user, count=5):
    """Loads the given Twitter search results and publishes them to the page."""
    search_url = "http://search.twitter.com/search.json?q=from:%s&rpp=%i" % (user, count)
    cache_key = "feeds.twitter_feed:%s" % search_url
    feed = cache.get(cache_key)
    if feed is None:
        try:
            response = urllib2.urlopen(search_url)
        except urllib2.URLError:
            feed = {}
        else:
            result = simplejson.load(response)
            items = [{"date": datetime.datetime.strptime(item["created_at"], "%a, %d %b %Y %H:%M:%S +0000"),
                      "title": item["text"]} for item in result["results"]]
            feed = {"items": items,
                    "title": "Twitter / %s" % user,
                    "url": "http://www.twitter.com/%s" % user}
        cache.set(cache_key, feed)
    context = {"feed": feed}
    return context

