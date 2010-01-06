"""Template tags used to adminstrate pages."""


from django.core.urlresolvers import reverse

from cms.apps.pages.admin import site, PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE
from cms.apps.pages.models import Page
from cms.apps.pages.templatetags import Library


register = Library()


@register.inclusion_tag("admin/sitemap.html", takes_context=True)
def sitemap(context):
    """Renders the admin sitemap."""
    request = context["request"]
    page_admin = site._registry[Page]
    try:
        homepage = Page.objects.get_homepage()
    except Page.DoesNotExist:
        homepage = None
    context = {"homepage": homepage,
               "request": request,
               "can_add": page_admin.has_add_permission(request),
               "can_change": page_admin.has_change_permission(request),
               "create_homepage_url": reverse("admin:pages_page_add") + "?%s=%s" % (PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE)}
    return context


@register.inclusion_tag("admin/sitemap_entry.html", takes_context=True)
def sitemap_entry(context, page):
    """Renders an entry in the sitemap."""
    # Extract required context variables.
    page_admin = site._registry[Page]
    request = context["request"]
    # Generate the new context.
    context = {"page": page,
               "parent": page.parent,
               "is_online": page.is_online,
               "children": page.children,
               "can_add": page_admin.has_add_permission(request),
               "can_change": page_admin.has_change_permission(request, page),
               "can_delete": page_admin.has_delete_permission(request, page),
               "can_move": page_admin.has_move_permission(request, page),
               "add_url": reverse("admin:pages_page_add") + "?%s=%s&parent=%i" % (PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE, page.id),
               "change_url": reverse("admin:pages_page_change", args=(page.pk,)) + "?%s=%s" % (PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE),
               "delete_url": reverse("admin:pages_page_delete", args=(page.pk,)) + "?%s=%s" % (PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE),
               "request": request}
    # Render the sitemap entry.
    return context

