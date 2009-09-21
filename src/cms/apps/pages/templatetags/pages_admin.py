"""Template tags used to adminstrate pages."""


from django.core.urlresolvers import reverse

from cms.apps.pages.admin import PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE
from cms.apps.pages.templatetags import Library


register = Library()


@register.inclusion_tag("admin/sitemap_entry.html", takes_context=True)
def sitemap_entry(context, page):
    """Renders an entry in the sitemap."""
    # Extract required context variables.
    page_admin = context["page_admin"]
    request = context["request"]
    # Generate the new context.
    context = {"page": page,
               "parent": page.parent,
               "is_online": page.is_online,
               "children": page.children,
               "can_add": page_admin.has_add_permission(request),
               "can_change": page_admin.has_change_permission(request, page),
               "can_delete": page_admin.has_delete_permission(request, page),
               "add_url": reverse("admin:pages_page_add") + "?%s=%s&parent=%i" % (PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE, page.id),
               "change_url": reverse("admin:pages_page_change", args=(page.pk,)) + "?%s=%s" % (PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE),
               "delete_url": reverse("admin:pages_page_delete", args=(page.pk,)) + "?%s=%s" % (PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE),
               "page_admin": page_admin,
               "request": request}
    # Render the sitemap entry.
    return context

