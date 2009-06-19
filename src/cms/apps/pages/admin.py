"""
The upgraded CMS online admin area.

This is an enhanced version of the Django admin area, providing a more
user-friendly appearance and providing additional functionality over the
standard implementation.
"""

import urllib

from django import forms, template
from django.core.urlresolvers import reverse
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response

from cms.apps.pages.forms import EditDetailsForm
from cms.apps.pages.models import Page


class AdminSite(admin.AdminSite):
    
    """The CMS admin site."""
    
    def root(self, request, url):
        """Adds additional views to the admin site."""
        if url == "edit-details/":
            return self.edit_details(request)
        
        return super(AdminSite, self).root(request, url)
        
    def index(self, request, extra_context=None):
        """Displays the admin site dashboard."""
        context = {"title": "Dashboard"}
        context.update(extra_context or {})
        return super(AdminSite, self).index(request, context)
    
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
                    return HttpResponseRedirect("./")
                else:
                    return HttpResponseRedirect("../")
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
        
    
# The default instance of the CMS admin site.
    
site = AdminSite()


class PageBaseAdmin(admin.ModelAdmin):
    
    """Base admin class for Content models."""
    
    date_hierarchy = "last_modified"
    
    seo_fieldsets = (("Search engine optimization", {"fields": ("browser_title", "meta_keywords", "meta_description", "sitemap_priority", "sitemap_change_frequency", "robots_allow_indexing", "robots_allow_archiving", "robots_follow_links",),
                                                     "classes": ("collapse",),},),)
    
    publication_fieldsets = (("Publication", {"fields": ("publication_date", "expiry_date", "is_online",),
                                              "classes": ("collapse",)}),)

    navigation_fieldsets = (("Navigation", {"fields": ("short_title",),
                                            "classes": ("collapse",),}))

    fieldsets = ((None, {"fields": ("title", "url_title",),},),) + navigation_fieldsets + publication_fieldsets + seo_fieldsets
    
    list_display = ("title", "is_online", "last_modified",)
    
    list_filter = ("is_online",)
    
    prepopulated_fields = {"url_title": ("title",),}
    
    search_fields = ("title", "browser_title",)
    
    
PAGE_TYPE_PARAMETER = "type"
    

class PageAdmin(PageBaseAdmin):

    """Admin settings for Page models."""

    fieldsets = ((None, {"fields": ("title", "url_title", "parent",),},),
                 ("Navigation", {"fields": ("short_title", "in_navigation",),
                                 "classes": ("collapse",),},),) + PageBaseAdmin.publication_fieldsets + PageBaseAdmin.seo_fieldsets

    # Custom admin views.
    
    def add_view(self, request, *args, **kwargs):
        """Ensures that a valid content type is chosen."""
        if not PAGE_TYPE_PARAMETER in request.GET:
            # Generate the available content items.
            content_items = self.model.content_registry.items()
            content_items.sort(lambda a, b: cmp(a[1].verbose_name, b[1].verbose_name))
            content_types = []
            for slug, content_type in content_items:
                get_params = request.GET.items()
                get_params.append((PAGE_TYPE_PARAMETER, slug))
                query_string = urllib.urlencode(get_params)
                url = request.path + "?" + query_string
                content_type_context = {"name": content_type.verbose_name,
                                        "icon": content_type.icon,
                                        "url": url}
                content_types.append(content_type_context)
            # Shortcut for when there is a single content type.
            if len(content_types) == 1:
                return HttpResponseRedirect(content_types[0]["url"])
            # Render the select page template.
            context = {"title": "Select page type",
                       "content_types": content_types,
                       "root_path": self.admin_site.root_path}
            return render_to_response("admin/pages/page/select_page_type.html", context, template.RequestContext(request))
        return super(PageAdmin, self).add_view(request, *args, **kwargs)

    # Plugable content methods.

    def get_page_content_type(self, request, obj=None):
        """Retrieves the page content type slug."""
        if PAGE_TYPE_PARAMETER in request.GET:
            return request.GET[PAGE_TYPE_PARAMETER]
        if obj and obj.content_type:
            return obj.content_type
        raise Http404, "You must specify a page content type."

    def get_page_content(self, request, obj=None):
        """Retrieves the page content object."""
        page_content_type = self.get_page_content_type(request, obj)
        page_content_cls = self.model.lookup_content(page_content_type)
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
        PageForm = super(PageAdmin, self).get_form(request, obj, **defaults)
        # HACK: Need to limit parents field based on object. This should be done in
        # formfield_for_foreignkey, but that method does not know about the object instance.
        valid_parents = Page.objects.all()
        if obj:
            invalid_parents = [child.id for child in obj.all_children] + [obj.id]
            valid_parents = valid_parents.exclude(id__in=invalid_parents)
        if valid_parents:
            parent_choices = [(parent.id, u" \u203a ".join([unicode(breadcrumb) for breadcrumb in parent.breadcrumbs]))
                              for parent in valid_parents]
        else:
            parent_choices = (("", "---------"),)
        PageForm.base_fields["parent"].choices = parent_choices
        # Return the completed form.
        return PageForm

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

