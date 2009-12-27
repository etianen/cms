"""
The upgraded CMS online admin area.

This is an enhanced version of the Django admin area, providing a more
user-friendly appearance and providing additional functionality over the
standard implementation.
"""

from __future__ import with_statement

import urllib, functools

from django import template
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.conf.urls.defaults import patterns, url
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import User
from django.db import transaction
from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.shortcuts import render_to_response, redirect

from reversion.admin import VersionAdmin

from cms.apps.pages import content
from cms.apps.pages.forms import EditDetailsForm
from cms.apps.pages.models import Page
from cms.apps.pages.models.managers import publication_manager


# The GET parameter used to indicate where page admin actions originated.
PAGE_FROM_KEY = "from"


# The GET parameter value used to indicate that the page admin action came form the sitemap.
PAGE_FROM_SITEMAP_VALUE = "sitemap"


class AdminSite(admin.AdminSite):
    
    """The CMS admin site."""
    
    index_template = "admin/dashboard.html"
    
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
                               url(r"^edit-details/$", self.admin_view(self.edit_details), name="edit_details"),
                               url(r"^move-page/$", self.admin_view(self.move_page), name="move_page"),
                               url(r"^tinymce-init.js$", self.admin_view(self.tinymce_init), name="tinymce_init"),)
        return custom_urls + urls
        
    @transaction.commit_on_success
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
                   "create_homepage_url": reverse("admin:pages_page_add") + "?%s=%s" % (PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE)}
        context.update(extra_context or {})
        # Render the index page.
        return super(AdminSite, self).index(request, context)
    
    def move_page(self, request):
        """Moves a page up or down."""
        page = Page.objects.get_by_id(request.POST["page"])
        # Check that the user has permission to move the page.
        if not self._registry[Page].has_move_permission(request, page):
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
                # To prevent duplicating the order key, we need to do a little dance here.
                page_order = page.order
                other_order = other.order
                page.order = None
                page.save()
                other.order = page_order
                other.save()
                page.order = other_order
                page.save()
        # Return a response appropriate to whether this was an AJAX request or not.
        if request.is_ajax():
            return HttpResponse("Page #%s was moved %s." % (page.id, direction))
        else:
            return redirect("admin:index")
    
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
                    return redirect("admin:edit_details")
                else:
                    return redirect("admin:index")
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
                   "app_label": User._meta.app_label,}
        return render_to_response("admin/edit_details_form.html", context, template.RequestContext(request))
    
    def tinymce_init(self, request):
        """Renders the TinyMCE initialization script."""
        context = {"TINYMCE_CONTENT_CSS": settings.TINYMCE_CONTENT_CSS}
        return render_to_response("admin/tinymce_init.js", context, template.RequestContext(request), mimetype="text/javascript")
        
    
# The default instance of the CMS admin site.
site = AdminSite()


# Page admin classes.


class PublishedModelAdmin(admin.ModelAdmin):
    
    """Base admin class for published models."""
    
    actions = ("publish_selected", "unpublish_selected",)
    
    change_form_template = "admin/pages/publishedmodel/change_form.html"
    
    publication_fieldsets = (("Publication", {"fields": ("is_online",),
                                              "classes": ("collapse",),}),)
    
    list_filter = ("is_online",)
    
    # Custom admin actions.
    
    def publish_selected(self, request, queryset):
        """Publishes the selected models."""
        queryset.update(is_online=True)
    publish_selected.short_description = "Place selected %(verbose_name_plural)s online"
    
    def unpublish_selected(self, request, queryset):
        """Unpublishes the selected models."""
        queryset.update(is_online=False)
    unpublish_selected.short_description = "Take selected %(verbose_name_plural)s offline"


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
        # Create the page content.
        page_content_type = self.get_page_content_type(request, obj)
        page_content = self.get_page_content(request, obj)
        for field_name in page_content.get_field_names():
            field_data = form.cleaned_data[field_name]
            setattr(page_content, field_name, field_data)
        obj.content_type = page_content_type
        obj.content = page_content
        # Save the model.
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
                return redirect("admin:index")
        return super(PageAdmin, self).changelist_view(request, *args, **kwargs)
    
    def has_add_content_permission(self, request, slug):
        """Checks whether the given user can edit the given content slug."""
        model = self.model
        opts = model._meta
        # The default page add permission implicitly allows editing of the default content type.
        if slug == settings.DEFAULT_CONTENT_REGISTRATION_KEY:
            return True
        # Check user has correct permission.
        add_permission = "%s.%s" % (opts.app_label, content.get_add_permission(slug))
        return request.user.has_perm(add_permission)
    
    def has_move_permission(self, request, obj):
        """Checks whether the given user can move the given page."""
        return self.has_change_permission(request, obj.parent)
    
    def add_view(self, request, *args, **kwargs):
        """Ensures that a valid content type is chosen."""
        if not PAGE_TYPE_PARAMETER in request.GET:
            # Generate the available content items.
            content_items = content.registered_content.items()
            content_items.sort(lambda a, b: cmp(a[1].classifier, b[1].classifier) or cmp(a[1].verbose_name.lower(), b[1].verbose_name.lower()))
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
                return redirect(content_types[0]["url"])
            # Render the select page template.
            context = {"title": "Select page type",
                       "content_types": content_types}
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

