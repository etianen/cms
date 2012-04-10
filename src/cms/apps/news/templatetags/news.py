"""Template tags used by the news module."""

from django import template


register = template.Library()


@register.inclusion_tag("news/includes/article_list.html", takes_context=True)
def article_list(context, articles):
    """Renders a list of news articles."""
    request = context["request"]
    pages = context["pages"]
    return {
        "articles": articles,
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
        "article": article,
        "url": url,
    }