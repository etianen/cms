"""Template tags used to adminstrate pages."""


from django import template
from django.core.urlresolvers import reverse

from cms.apps.pages.admin import site, PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE
from cms.apps.pages.models import Page
from cms.apps.pages.templatetags import PatternNode


register = template.Library()


@register.tag
def sitemap(parser, token):
    """
    Renders the admin sitemap::
    
        {% sitemap %}
        
    """
    def handler(context):
        request = context["request"]
        page_admin = site._registry[Page]
        try:
            homepage = Page.objects.get_homepage()
        except Page.DoesNotExist:
            homepage = None
        # Render the sitemap.
        context.push()
        try:
            context.update({"homepage": homepage,
                            "can_add": page_admin.has_add_permission(request),
                            "can_change": page_admin.has_change_permission(request),
                            "create_homepage_url": reverse("admin:pages_page_add") + "?%s=%s" % (PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE)})
            return template.loader.render_to_string("admin/sitemap.html", context)
        finally:
            context.pop()
    return PatternNode(parser, token, handler, ("",))


@register.tag
def sitemap_entry(parser, token):
    """
    Renders an entry in the sitemap::
        
        {% sitemap_entry page %}
    
    """
    def handler(context, page):
        # Extract required context variables.
        page_admin = site._registry[Page]
        request = context["request"]
        # Render the entry.
        context.push()
        try:
            context.update({"page": page,
                            "can_change": page_admin.has_change_permission(request, page),
                            "can_delete": page_admin.has_delete_permission(request, page),
                            "can_move": page_admin.has_move_permission(request, page),
                            "add_url": reverse("admin:pages_page_add") + "?%s=%s&parent=%i" % (PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE, page.id),
                            "change_url": reverse("admin:pages_page_change", args=(page.pk,)) + "?%s=%s" % (PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE),
                            "delete_url": reverse("admin:pages_page_delete", args=(page.pk,)) + "?%s=%s" % (PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE),})
            return template.loader.render_to_string("admin/sitemap_entry.html", context)
        finally:
            context.pop()
    return PatternNode(parser, token, handler, ("{page}",))

