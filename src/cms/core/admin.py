"""
The upgraded CMS online admin area.

This is an enhanced version of the Django admin area, providing a more
user-friendly appearance and providing additional functionality over the
standard implementation.
"""


from django import template
from django.core.urlresolvers import reverse
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import redirect, render_to_response

from cms.core.forms import EditDetailsForm
from cms.core.views import permalink_redirect


class AdminSite(admin.AdminSite):
    
    """The CMS admin site."""
    
    # HACK: The base admin site manually sets the root path to a wrong value,
    # thus this hack has to remain until the base admin site fixes this.
    def __init__(self, *args, **kwargs):
        """Initializes the admin site."""
        super(AdminSite, self).__init__(*args, **kwargs)
        self.root_path = "/admin/"
    
    def index(self, request, extra_context=None):
        """Displays the admin site dashboard."""
        context = {"title": "Dashboard"}
        context.update(extra_context or {})
        return super(AdminSite, self).index(request, context)
    
    # Custom admin views.
    
    def get_urls(self):
        """Adds some custom functionality to the admin site."""
        urlpatterns = patterns("",
                               url(r"^edit-details/$", self.admin_view(self.edit_details), name="admin_edit_details"),
                               url(r"^tiny-mce-init.js$", self.admin_view(self.tiny_mce_init), name="admin_tiny_mce_init"),
                               # HACK: This might not actually be needed if custom view on site urls are used for content objects.
                               url(r"^r/(\d+)/(.+)/$", self.admin_view(permalink_redirect), name="admin_view_on_site"),)
        urlpatterns += super(AdminSite, self).get_urls()
        return urlpatterns
    
    def edit_details(self, request):
        """Allows a user to edit their own details."""
        user = request.user
        if request.method == "POST":
            form = EditDetailsForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                message = "Your details have been updated."
                request.user.message_set.create(message=message)
                if "_continue" in request.POST:
                    return redirect("admin_edit_details")
                else:
                    return redirect("admin_index")
        else:
            form = EditDetailsForm(instance=user)
        media = form.media
        context = {"title": "Edit details",
                   "form": form,
                   "is_popup": False,
                   "add": False,
                   "change": True,
                   "has_add_permission": False,
                   "has_delete_permission": False,
                   "has_change_permission": True,
                   "has_file_field": False,
                   "has_absolute_url": False,
                   "auto_populated_fields": (),
                   "opts": User._meta,
                   "media": media,
                   "save_as": False,
                   "root_path": self.root_path,
                   "app_label": User._meta.app_label,}
        return render_to_response("admin/edit_details_form.html", context, template.RequestContext(request))
    
    def tiny_mce_init(self, request):
        """Renders the TinyMCE initialization script."""
        context = {}
        return render_to_response("admin/tiny_mce_init.js", context, template.RequestContext(request), mimetype="text/javascript")
    
    
# The default instance of the CMS admin site.
    
site = AdminSite()


class ContentAdmin(admin.ModelAdmin):
    
    """Base admin class for Content models."""
    
    date_hierarchy = "last_modified"
    
    seo_fieldsets = (("Search engine optimization", {"fields": ("browser_title", "keywords", "description", "priority", "change_frequency", "allow_indexing", "allow_archiving", "follow_links",),
                                                     "classes": ("collapse",),},),)
    
    fieldsets = ((None, {"fields": ("title", "is_online",),},),) + seo_fieldsets
    
    list_display = ("title", "is_online",)
    
    search_fields = ("title", "browser_title",)
    
    list_filter = ("is_online",)
    
