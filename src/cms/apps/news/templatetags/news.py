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
def category_url(context, category):
    """Renders the URL for the given category."""
    pages = context["pages"]
    page = pages.current
    return escape(category.get_permalink_for_page(page))
    
    
@register.inclusion_tag("news/includes/category_list.html", takes_context=True)
def category_list(context, category_list):
    """Renders a list of categories."""
    pages = context["pages"]
    page = pages.current
    category = context.get("category", None)
    article_archive_url = page.reverse("article_archive")
    return {
        "category_list": category_list,
        "category": category,
        "pages": pages,
        "article_archive_url": article_archive_url,
        "current_category": category,
    }