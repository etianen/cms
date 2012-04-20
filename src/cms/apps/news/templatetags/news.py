"""Template tags used by the news module."""

from django import template
from django.utils.html import escape

from cms.apps.pages.models import Page
from cms.apps.news.models import Article, get_default_news_feed, NewsFeed


register = template.Library()


@register.inclusion_tag("news/includes/article_list.html", takes_context=True)
def article_list(context, article_list):
    """Renders a list of news articles."""
    request = context["request"]
    pages = context["pages"]
    page_obj = context.get("page_obj")
    return {
        "article_list": article_list,
        "request": request,
        "pages": pages,
        "page_obj": page_obj,
    }
    
    
@register.simple_tag(takes_context=True)
def article_url(context, article):
    """Renders the URL for an article."""
    pages = context["pages"]
    page = pages.current
    return escape(article.get_permalink_for_page(page))
    
    
@register.inclusion_tag("news/includes/article_list_item.html", takes_context=True)
def article_list_item(context, article):
    """Renders an item in an article list."""
    pages = context["pages"]
    return {
        "pages": pages,
        "article": article,
    }


@register.simple_tag(takes_context=True)
def article_archive_url(context):
    """Renders the URL for the current article archive."""
    pages = context["pages"]
    page = pages.current
    return escape(page.reverse("article_archive"))


@register.simple_tag(takes_context=True)
def category_url(context, category):
    """Renders the URL for the given category."""
    pages = context["pages"]
    page = pages.current
    return escape(category.get_permalink_for_page(page))
    
    
@register.inclusion_tag("news/includes/category_list.html", takes_context=True)
def category_list(context, category_list):
    """Renders a list of categories."""
    pages = context["pages"]
    category = context.get("category", None)
    return {
        "category_list": category_list,
        "category": category,
        "pages": pages,
        "current_category": category,
    }
    
    
@register.simple_tag(takes_context=True)
def article_year_archive_url(context, year):
    """Renders the year archive URL for the given year."""
    pages = context["pages"]
    page = pages.current
    return escape(page.reverse("article_year_archive", kwargs={
        "year": year,
    }))
    
    
@register.simple_tag(takes_context=True)
def article_day_archive_url(context, date):
    """Renders the month archive URL for the given date."""
    pages = context["pages"]
    page = pages.current
    return escape(page.reverse("article_day_archive", kwargs={
        "year": date.year,
        "month": date.strftime("%b").lower(),
        "day": date.day,
    }))
    
    
@register.inclusion_tag("news/includes/article_date.html", takes_context=True)
def article_date(context, article):
    """Renders a rich date for the given article."""
    pages = context["pages"]
    return {
        "article": article,
        "pages": pages,
    }
    
    
@register.inclusion_tag("news/includes/article_category_list.html", takes_context=True)
def article_category_list(context, article):
    """Renders the list of article categories."""
    pages = context["pages"]
    return {
        "article": article,
        "pages": pages,
        "categories": article.categories.all(),
    }
    
    
@register.inclusion_tag("news/includes/article_meta.html", takes_context=True)
def article_meta(context, article):
    pages = context["pages"]
    return {
        "article": article,
        "pages": pages,
    }
    
    
@register.inclusion_tag("news/includes/article_date_list.html", takes_context=True)
def article_date_list(context, date_list):
    """Renders a list of dates."""
    pages = context["pages"]
    # Resolve the current year.
    current_year = context.get("year", None)
    if current_year is not None:
        current_year = int(current_year)
    else:
        current_month = context.get("month", None)
        if current_month is not None:
            current_year = current_month.year
        else:
            current_day = context.get("day", None)
            if current_day is not None:
                current_year = current_day.year
            else:
                current_article = context.get("article", None)
                if current_article is not None:
                    current_year = current_article.date.year
    # Render the template.
    return {
        "pages": pages,
        "date_list": date_list,
        "current_year": current_year,
    }
    
    
@register.inclusion_tag("news/includes/article_latest_list.html", takes_context=True)
def article_latest_list(context, page=None, limit=5):
    """Renders a widget-style list of latest articles."""
    pages = context["pages"]
    # Resolve the page and news feed.
    if page is None:
        news_feed = get_default_news_feed()
        page = news_feed.page
    elif isinstance(page, Page):
        news_feed = page.content
    elif isinstance(page, NewsFeed):
        news_feed = page
        page = news_feed.page
    elif isinstance(page, int):
        news_feed = NewsFeed.objects.get(id=page)
        page = news_feed.page
    else:
        raise ValueError("{!r} is not a valid news feed identifier".format(page))
    # Load the articles.
    article_list = Article.objects.filter(
        news_feed = news_feed,
    )[:limit]
    # Given them the page (for efficiency).
    for article in article_list:
        article.page = page
    return {
        "article_list": article_list,
        "pages": pages,
        "page": page,
    }