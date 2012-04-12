"""Template tags used by the news module."""

from django import template
from django.utils.html import escape


register = template.Library()


@register.inclusion_tag("news/includes/article_list.html", takes_context=True)
def article_list(context, article_list):
    """Renders a list of news articles."""
    request = context["request"]
    pages = context["pages"]
    return {
        "article_list": article_list,
        "request": request,
        "pages": pages,
    }
    
    
@register.inclusion_tag("news/includes/article_list_item.html", takes_context=True)
def article_list_item(context, article):
    """Renders an item in an article list."""
    pages = context["pages"]
    page = pages.current
    # Calculate the URL rather than have to look up the article page AGAIN.
    url = page.reverse("article_detail", kwargs={
        "year": article.date.year,
        "month": article.date.strftime("%b").lower(),
        "day": article.date.day,
        "url_title": article.url_title,
    })
    return {
        "pages": context["pages"],
        "article": article,
        "url": url,
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
    current_year = context.get("year", None)
    if current_year is not None:
        current_year = int(current_year)
    return {
        "pages": pages,
        "date_list": date_list,
        "current_year": current_year,
    }