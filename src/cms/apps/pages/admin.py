"""
The upgraded CMS online admin area.

This is an enhanced version of the Django admin area, providing a more
user-friendly appearance and providing additional functionality over the
standard implementation.
"""

import urllib

from django import forms, template
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response

from reversion.admin import VersionAdmin

from cms.apps.pages import content
from cms.apps.pages.forms import EditDetailsForm
from cms.apps.pages.models import Page


# The GET parameter used to indicate where page admin actions originated.
PAGE_FROM_KEY = "from"


# The GET parameter value used to indicate that the page admin action came form the sitemap.
PAGE_FROM_SITEMAP_VALUE = "sitemap"


class AdminSite(admin.AdminSite):
    
    """The CMS admin site."""
    
    index_template = "admin/dashboard.html"
    
    def root(self, request, url):
        """Adds additional views to the admin site."""
        if url == "edit-details/":
            return self.edit_details(request)
        return super(AdminSite, self).root(request, url)
        
    def index(self, request, extra_context=None):
        """Displays the admin site dashboard."""
        # Retrieve the homepage in order to render the sitemap.
        try:
            homepage = Page.objects.get_homepage()
        except Page.DoesNotExist:
            homepage = None
        # Generate the context.
        context = {"title": "Dashboard",
                   "homepage": homepage,
                   "page_admin": self._registry[Page],
                   "create_homepage_url": self.root_path + "pages/page/add/?%s=%s" % (PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE)}
        context.update(extra_context or {})
        # Render the index page.
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


# Page admin classes.


class PublishedModelAdmin(admin.ModelAdmin):
    
    """Base admin class for published models."""
    
    change_form_template = "admin/pages/publishedmodel/change_form.html"
    
    publication_fieldsets = (("Publication", {"fields": ("is_online",),
                                              "classes": ("collapse",),}),)
    
    list_filter = ("is_online",)


class PageBaseAdmin(VersionAdmin, PublishedModelAdmin):
    
    """Base admin class for ArticleBase models."""
    
    date_hierarchy = "last_modified"
    
    base_fieldsets = ((None, {"fields": ("title", "url_title",),},),)
    
    navigation_fieldsets = (("Navigation", {"fields": ("short_title",),
                                            "classes": ("collapse",),}),)
    
    seo_fieldsets = (("Search engine optimization", {"fields": ("browser_title", "meta_keywords", "meta_description", "robots_index", "robots_archive", "robots_follow", "sitemap_priority", "sitemap_changefreq",),
                                                     "classes": ("collapse",),},),)
    
    fieldsets = base_fieldsets + PublishedModelAdmin.publication_fieldsets + navigation_fieldsets + seo_fieldsets

    list_display = ("title", "last_modified", "is_online",)
    
    prepopulated_fields = {"url_title": ("title",),}
    
    search_fields = ("title",)
    
    ordering = ("title",)


# The GET parameter used to indicate content type.
PAGE_TYPE_PARAMETER = "type"
    
    
class PageAdmin(PageBaseAdmin):

    """Admin settings for Page models."""

    publication_fieldsets = (("Publication", {"fields": ("publication_date", "expiry_date", "is_online",),
                                              "classes": ("collapse",)}),)

    navigation_fieldsets = (("Navigation", {"fields": ("short_title", "permalink", "in_navigation",),
                                            "classes": ("collapse",),},),)

    fieldsets = ((None, {"fields": ("title", "url_title", "parent",),},),) + publication_fieldsets + navigation_fieldsets + PageBaseAdmin.seo_fieldsets

    # Reversion

    def get_revision_form_data(self, request, obj, version):
        """
        Returns a dictionary of data to set in the admin form in order to revert
        to the given revision.
        """
        data = super(PageAdmin, self).get_revision_form_data(request, obj, version)
        content_data = version.object_version.object.content.data
        data.update(content_data)
        return data

    # Plugable content types.

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
        page_content_cls = content.lookup(page_content_type)
        # Create new page content instance.
        page_content = page_content_cls(obj)
        return page_content

    def get_fieldsets(self, request, obj=None):
        """Generates the custom content fieldsets."""
        page_content = self.get_page_content(request, obj)
        content_fieldsets = page_content.get_fieldsets()
        fieldsets = super(PageBaseAdmin, self).get_fieldsets(request, obj)
        fieldsets = fieldsets[0:1] + content_fieldsets + fieldsets[1:]
        return fieldsets

    def get_form(self, request, obj=None, **kwargs):
        """Adds the template area fields to the form."""
        page_content = self.get_page_content(request, obj)
        Form = page_content.get_form()
        defaults = {"form": Form}
        defaults.update(kwargs)
        PageForm = super(PageAdmin, self).get_form(request, obj, **defaults)
        # HACK: Need to limit parents field based on object. This should be done in
        # formfield_for_foreignkey, but that method does not know about the object instance.
        if obj:
            invalid_parents = frozenset(obj.all_children + [obj])
        else:
            invalid_parents = frozenset()
        try:
            homepage = Page.objects.get_homepage()
        except Page.DoesNotExist:
            parent_choices = []
        else:
            parent_choices = []
            for page in [homepage] + homepage.all_children:
                if not page in invalid_parents:
                    parent_choices.append((page.id, u" \u203a ".join([unicode(breadcrumb) for breadcrumb in list(reversed(page.all_parents)) + [page]])))
        if not parent_choices:
            parent_choices = (("", "---------"),)
        PageForm.base_fields["parent"].choices = parent_choices
        # Return the completed form.
        return PageForm

    def save_model(self, request, obj, form, change):
        """Saves the model and adds its content fields."""
        page_content_type = self.get_page_content_type(request, obj)
        page_content = self.get_page_content(request, obj)
        for field_name in page_content.get_field_names():
            field_data = form.cleaned_data[field_name]
            setattr(page_content, field_name, field_data)
        obj.content_type = page_content_type
        obj.content = page_content
        super(PageBaseAdmin, self).save_model(request, obj, form, change)
        # Set the default ordering of the page to its id.
        if not change:
            obj.order = obj.id
            obj.save()

    # Custom views.

    def patch_response_location(self, request, response):
        """Perpetuates the 'from' key in all redirect responses."""
        if isinstance(response, HttpResponseRedirect):
            if PAGE_FROM_KEY in request.GET:
                response["Location"] += "?%s=%s" % (PAGE_FROM_KEY, request.GET[PAGE_FROM_KEY])
        return response
            
    def changelist_view(self, request, *args, **kwargs):
        """Redirects to the sitemap, if appropriate."""
        if PAGE_FROM_KEY in request.GET:
            redirect_slug = request.GET[PAGE_FROM_KEY]
            if redirect_slug == PAGE_FROM_SITEMAP_VALUE:
                return HttpResponseRedirect(self.admin_site.root_path)
        return super(PageAdmin, self).changelist_view(request, *args, **kwargs)
    
    def has_add_content_permission(self, request, slug):
        """Checks whether the given user can edit the given content slug."""
        model = self.model
        opts = model._meta
        # The default page add permission implicitly allows editing of the default content type.
        if slug == content.DEFAULT_CONTENT_SLUG:
            return True
        # Check user has correct permission.
        add_permission = "%s.%s" % (opts.app_label, content.get_add_permission(slug))
        return request.user.has_perm(add_permission)
    
    def add_view(self, request, *args, **kwargs):
        """Ensures that a valid content type is chosen."""
        model = self.model
        opts = model._meta
        user = request.user
        if not PAGE_TYPE_PARAMETER in request.GET:
            # Generate the available content items.
            content_items = content.registered_content.items()
            content_items.sort(lambda a, b: cmp(a[1].classifier, b[1].classifier) or cmp(a[1].verbose_name, b[1].verbose_name))
            content_types = []
            for slug, content_type in content_items:
                if self.has_add_content_permission(request, slug):
                    # If we get this far, then we have permisison to add a page of this type.
                    get_params = request.GET.items()
                    get_params.append((PAGE_TYPE_PARAMETER, slug))
                    query_string = urllib.urlencode(get_params)
                    url = request.path + "?" + query_string
                    content_type_context = {"name": content_type.verbose_name,
                                            "icon": content_type.icon,
                                            "url": url,
                                            "classifier": content_type.classifier}
                    content_types.append(content_type_context)
            # Shortcut for when there is a single content type.
            if len(content_types) == 1:
                return HttpResponseRedirect(content_types[0]["url"])
            # Render the select page template.
            context = {"title": "Select page type",
                       "content_types": content_types,
                       "root_path": self.admin_site.root_path}
            return render_to_response("admin/pages/page/select_page_type.html", context, template.RequestContext(request))
        else:
            if not self.has_add_content_permission(request, request.GET[PAGE_TYPE_PARAMETER]):
                raise PermissionDenied, "You are not allowed to add pages of that content type."
        return super(PageBaseAdmin, self).add_view(request, *args, **kwargs)
    
    def response_add(self, request, *args, **kwargs):
        """Redirects to the sitemap if appropriate."""
        response = super(PageAdmin, self).response_add(request, *args, **kwargs)
        return self.patch_response_location(request, response)
    
    def response_change(self, request, *args, **kwargs):
        """Redirects to the sitemap if appropriate."""
        response = super(PageAdmin, self).response_change(request, *args, **kwargs)
        return self.patch_response_location(request, response)
    
    def delete_view(self, request, *args, **kwargs):
        """Redirects to the sitemap if appropriate."""
        response = super(PageAdmin, self).delete_view(request, *args, **kwargs)
        return self.patch_response_location(request, response)


site.register(Page, PageAdmin)

