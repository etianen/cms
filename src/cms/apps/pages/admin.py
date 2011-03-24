"""
The upgraded CMS online admin area.

This is an enhanced version of the Django admin area, providing a more
user-friendly appearance and providing additional functionality over the
standard implementation.
"""

from __future__ import with_statement

import urllib, json

from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.conf.urls.defaults import patterns, url
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.http import Http404, HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect

from cms.core import debug
from cms.core.admin import PageBaseAdmin, site, PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE
from cms.core.db import locked
from cms.apps.pages.models import Page, get_registered_content


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
            return ContentType.objects.get_for_id(request.GET[PAGE_TYPE_PARAMETER]).model_class()
        if obj and obj.content_type:
            return obj.content_type
        raise Http404, "You must specify a page content type."

    def get_fieldsets(self, request, obj=None):
        """Generates the custom content fieldsets."""
        page_content = self.get_page_content(request, obj)
        content_fieldsets = page_content.get_fieldsets()
        fieldsets = super(PageBaseAdmin, self).get_fieldsets(request, obj)
        fieldsets = fieldsets[0:1] + content_fieldsets + fieldsets[1:]
        return fieldsets

    def get_form(self, request, obj=None, **kwargs):
        """Adds the template area fields to the form."""
        content_cls = self.get_page_content(request, obj)
        Form = page_content.get_form()
        defaults = {"form": Form}
        defaults.update(kwargs)
        PageForm = super(PageAdmin, self).get_form(request, obj, **defaults)
        # HACK: Need to limit parents field based on object. This should be done in
        # formfield_for_foreignkey, but that method does not know about the object instance.
        if obj:
            invalid_parents = set(child.id for child in obj.children)
            invalid_parents.add(obj.id)
        else:
            invalid_parents = frozenset()
        try:
            homepage = Page.objects.get_homepage()
        except Page.DoesNotExist:
            parent_choices = []
        else:
            parent_choices = []
            for page in [homepage] + homepage.all_children:
                if not page.id in invalid_parents:
                    parent_choices.append((page.id, u" \u203a ".join(unicode(breadcrumb) for breadcrumb in page.breadcrumbs)))
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
        # Get the page order.
        if not obj.order:
            with locked(Page):
                try:
                    obj.order = self.model.objects.order_by("-order").values_list("order", flat=True)[0] + 1
                except IndexError:
                    obj.order = 1
        # Save the model.
        super(PageBaseAdmin, self).save_model(request, obj, form, change)

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
    
    def has_add_content_permission(self, request, model):
        """Checks whether the given user can edit the given content model."""
        opts = model._meta
        return request.user.has_perm("{0}.{1}".format(opts.app_label, opts.get_add_permission()))
    
    def add_view(self, request, *args, **kwargs):
        """Ensures that a valid content type is chosen."""
        if not PAGE_TYPE_PARAMETER in request.GET:
            # Generate the available content items.
            content_items = get_registered_content()
            content_items.sort(lambda a, b: cmp(a.classifier, b.classifier) or cmp(a._meta.verbose_name.lower(), b._meta.verbose_name.lower()))
            content_types = []
            for content_type in content_items:
                if self.has_add_content_permission(request, content_type):
                    # If we get this far, then we have permisison to add a page of this type.
                    get_params = request.GET.copy()
                    get_params[PAGE_TYPE_PARAMETER] = ContentType.objects.get_for_model(content_type).id
                    query_string = get_params.urlencode()
                    url = request.path + "?" + query_string
                    content_type_context = {
                        "name": content_type._meta.verbose_name,
                        "icon": content_type.icon,
                        "url": url,
                        "classifier": content_type.classifier
                    }
                    content_types.append(content_type_context)
            # Shortcut for when there is a single content type.
            if len(content_types) == 1:
                return redirect(content_types[0]["url"])
            # Render the select page template.
            context = {"title": "Select page type",
                       "content_types": content_types}
            return render(request, "admin/pages/page/select_page_type.html", context)
        else:
            if not self.has_add_content_permission(request, ContentType.objects.get_for_id(request.GET[PAGE_TYPE_PARAMETER]).model_class()):
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
site.register_link_list(Page)