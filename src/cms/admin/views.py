"""Views used by the CMS admin extensions."""

from functools import wraps

from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseForbidden, HttpResponse
from django.utils import simplejson as json

from django.shortcuts import render, redirect

from cms import debug
from cms.models.managers import publication_manager


# The GET parameter used to indicate where page admin actions originated.
PAGE_FROM_KEY = "from"

# The GET parameter value used to indicate that the page admin action came form the sitemap.
PAGE_FROM_SITEMAP_VALUE = "sitemap"


def admin_view(view, *args, **kwargs):
    """Turns off publication management for admin views."""
    @wraps(view)
    def do_admin_view(*args, **kwargs):
        with publication_manager.select_published(False):
            return view(*args, **kwargs)
    return do_admin_view


def index(admin_site, request):
    """Renders the dashboard view."""
    response = admin_site.index(request)
    response.context_data["admin_site_template_name"] = response.template_name[0]
    response.template_name = "admin/dashboard.html"
    return response


def tinymce_init(admin_site, request):
    """Renders the tinymce init script."""
    return render(request, "admin/tinymce_init.js", {}, content_type="text/javascript; charset=utf-8")


@debug.print_exc
def sitemap_json(admin_site, request):
    """Returns a JSON data structure describing the sitemap."""
    # Get the homepage.
    page_model = request.pages.backend.model
    homepage = request.pages.homepage
    admin_opts = admin_site._registry[page_model]
    url_params = {
        "admin_name": admin_site.name,
        "app_label": page_model._meta.app_label,
        "model_name": page_model.__name__.lower(),
    }
    # Compile the initial data.
    data = {
        "canAdd": admin_opts.has_add_permission(request),
        "createHomepageUrl": reverse("{admin_name}:{app_label}_{model_name}_add".format(**url_params)) + "?{0}={1}".format(PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE),
        "moveUrl": request.pages.backend.can_move and reverse("admin:move_page") or None,
        "addUrl": reverse("{admin_name}:{app_label}_{model_name}_add".format(**url_params)) + "?{0}={1}&parent=__id__".format(PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE),
        "changeUrl": reverse("{admin_name}:{app_label}_{model_name}_change".format(**url_params), args=("__id__",)) + "?{0}={1}".format(PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE),
        "deleteUrl": reverse("{admin_name}:{app_label}_{model_name}_delete".format(**url_params), args=("__id__",)) + "?{0}={1}".format(PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE),
    }
    # Add in the page data.
    if homepage:
        def sitemap_entry(page):
            children = []
            for child in page.children:
                children.append(sitemap_entry(child))
            return {
                "isOnline": page.is_online,
                "id": page.id,
                "title": unicode(page),
                "children": children,
                "canChange": admin_opts.has_change_permission(request, page),
                "canDelete": admin_opts.has_delete_permission(request, page),
            }
        data["entries"] = [sitemap_entry(homepage)]
    else:
        data["entries"] = []
    # Render the JSON.
    response = HttpResponse(content_type="application/json; charset=utf-8")
    json.dump(data, response)
    return response
    
    
@transaction.commit_on_success
@debug.print_exc
def move_page(admin_site, request):
    """Moves a page up or down."""
    backend = request.pages.backend
    page = request.pages.get(int(request.POST["page"]))
    page_model = backend.model
    admin_opts = admin_site._registry[page_model]
    # Check that the user has permission to move the page.
    if not backend.can_move or not admin_opts.has_change_permission(request, page):
        return HttpResponseForbidden("You do not have permission to move this page.")
    # Do the swap.
    direction = request.POST["direction"]
    if direction == "up":
        backend.move_up(request, page)
    elif direction == "down":
        backend.move_down(request, page)
    else:
        raise ValueError("Direction should be 'up' or 'down'.")
    # Return a response appropriate to whether this was an AJAX request or not.
    if request.is_ajax():
        return HttpResponse("Page #%s was moved %s." % (page.id, direction))
    else:
        return redirect("admin:index")