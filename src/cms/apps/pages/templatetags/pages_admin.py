"""Template tags used to adminstrate pages."""


from django import template


register = template.Library()


@register.inclusion_tag("admin/sitemap_entry.html", takes_context=True)
def sitemap_entry(context, page):
    """Renders an entry in the sitemap."""
    # Extract required context variables.
    page_admin = context["page_admin"]
    request = context["request"]
    root_path = context["root_path"]
    # Generate the new context.
    page_admin_url = root_path + "pages/page/"
    change_url = page_admin_url + unicode(page.id) + "/"
    context = {"page": page,
               "parent": page.parent,
               "is_online": page.is_online,
               "children": page.children,
               "can_add": page_admin.has_add_permission(request),
               "can_change": page_admin.has_change_permission(request, page),
               "can_delete": page_admin.has_delete_permission(request, page),
               "add_url": page_admin_url + "add/?parent=" + unicode(page.id),
               "change_url": change_url,
               "delete_url": change_url + "delete/",
               "page_admin": page_admin,
               "request": request,
               "root_path": root_path}
    # Render the sitemap entry.
    return context

