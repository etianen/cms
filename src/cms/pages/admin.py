"""
The upgraded CMS online admin area.

This is an enhanced version of the Django admin area, providing a more
user-friendly appearance and providing additional functionality over the
standard implementation.
"""


from django import forms, template
from django.core.urlresolvers import reverse
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.http import Http404
from django.shortcuts import redirect, render_to_response

from cms.pages.forms import EditDetailsForm
from cms.pages.models import Page, get_page_content_type
from cms.pages.views import permalink_redirect


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
                               url(r"^tinymce-init.js$", self.admin_view(self.tiny_mce_init), name="admin_tinymce_init"),
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
        return render_to_response("admin/tinymce_init.js", context, template.RequestContext(request), mimetype="text/javascript")
        
    
# The default instance of the CMS admin site.
    
site = AdminSite()


class PageBaseAdmin(admin.ModelAdmin):
    
    """Base admin class for Content models."""
    
    date_hierarchy = "last_modified"
    
    seo_fieldsets = (("Search engine optimization", {"fields": ("browser_title", "keywords", "description", "priority", "change_frequency", "allow_indexing", "allow_archiving", "follow_links",),
                                                     "classes": ("collapse",),},),)
    
    publication_fieldsets = (("Publication", {"fields": ("publication_date", "expiry_date",),
                                              "classes": ("collapse",)}),)

    fieldsets = ((None, {"fields": ("title", "is_online",),},),) + publication_fieldsets + seo_fieldsets
    
    list_display = ("title", "is_online", "last_modified",)
    
    search_fields = ("title", "browser_title",)
    
    list_filter = ("is_online",)
    

class PageAdmin(PageBaseAdmin):

    """Admin settings for Page models."""

    fieldsets = ((None, {"fields": ("title", "url_title", "parent", "is_online",),},),
                 ("Navigation", {"fields": ("short_title", "in_navigation",),
                                 "classes": ("collapse",),},),) + PageBaseAdmin.publication_fieldsets + PageBaseAdmin.seo_fieldsets

    prepopulated_fields = {"url_title": ("title",),}

    def get_page_content_type(self, request, obj=None):
        """Retrieves the page content type slug."""
        if "type" in request.GET:
            return request.GET["type"]
        if obj and obj.content_type:
            return obj.content_type
        raise Http404, "You must specify a page content type."

    def get_page_content(self, request, obj=None):
        """Retrieves the page content object."""
        page_content_type = self.get_page_content_type(request, obj)
        page_content_cls = get_page_content_type(page_content_type)
        # Try to use an instance.
        if obj and obj.content:
            page_content_data = obj.content.data
        else:
            page_content_data = {}
        # Create new page content instance.
        page_content = page_content_cls(obj, page_content_data)
        return page_content

    def get_form(self, request, obj=None, **kwargs):
        """Adds the template area fields to the form."""
        page_content = self.get_page_content(request, obj)
        Form = page_content.get_form()
        defaults = {"form": Form}
        defaults.update(kwargs)
        return super(PageAdmin, self).get_form(request, obj, **defaults)

    def get_fieldsets(self, request, obj=None):
        """Generates the custom content fieldsets."""
        page_content = self.get_page_content(request, obj)
        content_fieldsets = page_content.get_fieldsets()
        fieldsets = super(PageAdmin, self).get_fieldsets(request, obj)
        fieldsets = fieldsets[0:1] + content_fieldsets + fieldsets[1:]
        return fieldsets

    def save_model(self, request, obj, form, change):
        """Saves the model and adds its content fields."""
        page_content_type = self.get_page_content_type(request, obj)
        page_content = self.get_page_content(request, obj)
        for field_name in page_content.get_field_names():
            field_data = form.cleaned_data[field_name]
            setattr(page_content, field_name, field_data)
        obj.content_type = page_content_type
        obj.content = page_content
        obj.save()


site.register(Page, PageAdmin)

