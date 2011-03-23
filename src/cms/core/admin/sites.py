"""Extensions to the Django admin site."""

from __future__ import with_statement

import functools, itertools, json

from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render

from cms.core import permalinks, debug
from cms.core.models.managers import publication_manager


# The GET parameter used to indicate where page admin actions originated.
PAGE_FROM_KEY = "from"

# The GET parameter value used to indicate that the page admin action came form the sitemap.
PAGE_FROM_SITEMAP_VALUE = "sitemap"


class AdminSite(admin.AdminSite):
    
    """The CMS admin site."""
    
    index_template = "admin/dashboard.html"
    
    def __init__(self, *args, **kwargs):
        """Initializes the admin site."""
        super(AdminSite, self).__init__(*args, **kwargs)
        self._link_list_models = set()
    
    def register_link_list(self, model):
        """Registers a model in the admin tinymce link list generator."""
        self._link_list_models.add(model)
        
    def unregister_link_list(self, model):
        """Removes a model from the admin tinymce link list generator."""
        self._link_list_models.remove(model)
    
    # Custom admin views.
    
    def admin_view(self, view, *args, **kwargs):
        """Turns off publication management for admin views."""
        view = super(AdminSite, self).admin_view(view, *args, **kwargs)
        @functools.wraps(view)
        def wrapper(*args, **kwargs):
            with publication_manager.select_published(False):
                return view(*args, **kwargs)
        return wrapper
    
    def get_urls(self):
        """Generates custom admin URLS."""
        urls = super(AdminSite, self).get_urls()
        custom_urls = patterns("",
            url(r"^tinymce-init.js$", self.admin_view(self.tinymce_init), name="tinymce_init"),
            url(r"^tinymce-link-list.js$", self.admin_view(self.tinymce_link_list), name="tinymce_link_list"),
            url(r"^sitemap.json$", self.admin_view(self.sitemap_json), name="sitemap_json"),
            url(r"^move-page/$", self.admin_view(self.move_page), name="move_page"),
        )
        return custom_urls + urls
    
    def tinymce_init(self, request):
        """Renders the tinymce init script."""
        return render(request, "admin/tinymce_init.js", {}, content_type="text/javascript; charset=utf-8")
    
    def tinymce_link_list(self, request):
        """Generates the tinymce link list."""
        generators = []
        for model in self._link_list_models:
            generators.append((unicode(obj), permalinks.create(obj)) for obj in model._default_manager.all().iterator())
        links = sorted(itertools.chain(*generators))
        context = {"links": links}
        return render(request, "admin/tinymce_link_list.js", context, mimetype="text/javascript")
    
    @debug.print_exc
    def sitemap_json(self, request):
        """Returns a JSON data structure describing the sitemap."""
        # Get the homepage.
        page_model = request.pages.backend.model
        homepage = request.pages.homepage
        admin_opts = self._registry[page_model]
        url_params = (page_model._meta.app_label, page_model.__name__.lower())
        # Compile the initial data.
        data = {
            "canAdd": admin_opts.has_add_permission(request),
            "canChange": admin_opts.has_change_permission(request),
            "canDelete": admin_opts.has_delete_permission(request),
            "createHomepageUrl": reverse("admin:{0}_{1}_add".format(*url_params)) + "?{0}={1}".format(PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE),
            "moveUrl": request.pages.backend.can_move and reverse("admin:move_page") or None,
            "addUrl": reverse("admin:{0}_{1}_add".format(*url_params)) + "?%s=%s&parent=__id__" % (PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE),
            "changeUrl": reverse("admin:{0}_{1}_change".format(*url_params), args=("__id__",)) + "?%s=%s" % (PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE),
            "deleteUrl": reverse("admin:{0}_{1}_delete".format(*url_params), args=("__id__",)) + "?%s=%s" % (PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE),
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
    def move_page(self, request):
        """Moves a page up or down."""
        page = Page.objects.get_page(request.POST["page"])
        # Check that the user has permission to move the page.
        if not self.has_change_permission(request, page):
            return HttpResponseForbidden("You do not have permission to move this page.")
        # Get the page to swap with.
        direction = request.POST["direction"]
        parent = page.parent
        if parent is not None:
            try:
                if direction == "up":
                    other = parent.children.order_by("-order").filter(order__lt=page.order)[0]
                elif direction == "down":
                    other = parent.children.order_by("order").filter(order__gt=page.order)[0]
                else:
                    raise ValueError, "Direction should be 'up' or 'down', not '%s'." % direction
            except IndexError:
                # Impossible to move pag up or down because it already is at the top or bottom!
                pass
            else:
                with locked(Page):
                    page_order = page.order
                    other_order = other.order
                    page.order = other_order
                    other.order = page_order
                    page.save()
                    other.save()
        # Return a response appropriate to whether this was an AJAX request or not.
        if request.is_ajax():
            return HttpResponse("Page #%s was moved %s." % (page.id, direction))
        else:
            return redirect("admin:index")