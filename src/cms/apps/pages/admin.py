"""
The upgraded CMS online admin area.

This is an enhanced version of the Django admin area, providing a more
user-friendly appearance and providing additional functionality over the
standard implementation.
"""

from __future__ import with_statement
import threading

from django.core.exceptions import PermissionDenied
from django.contrib.contenttypes.models import ContentType
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, redirect
from django import forms

from cms.admin import PageBaseAdmin, site, PAGE_FROM_KEY, PAGE_FROM_SITEMAP_VALUE
from cms.db import locked
from cms.apps.historylinks.models import HistoryLink
from cms.apps.pages.models import Page, get_registered_content


# The GET parameter used to indicate content type.
PAGE_TYPE_PARAMETER = "type"


# HACK: Used to provide thread safety for the patch inlines hack (below).
page_inlines_lock = threading.RLock()
    
    
class PageAdmin(PageBaseAdmin):

    """Admin settings for Page models."""

    fieldsets = (
        (None, {
            "fields": ("title", "url_title", "parent",),
        },),
        ("Publication", {
            "fields": ("publication_date", "expiry_date", "is_online",),
            "classes": ("collapse",),
        }),
        ("Navigation", {
            "fields": ("short_title", "permalink", "in_navigation",),
            "classes": ("collapse",),
        }),
        ("Search engine optimization", {
            "fields": ("browser_title", "meta_keywords", "meta_description", "sitemap_priority", "sitemap_changefreq", "robots_index", "robots_follow", "robots_archive",),
            "classes": ("collapse",),
        }),
    )
    
    def __init__(self, *args, **kwargs):
        """Initialzies the PageAdmin."""
        super(PageAdmin, self).__init__(*args, **kwargs)
        # Register all content classes with reversion.
        self.content_inline_instances = []
        for content_cls in get_registered_content():
            self._autoregister(content_cls, follow=["page"])
    
    def register_content_inline(self, content_cls, inline, inline_admin):
        """Registers an inline model with the page admin."""
        # Register the admin class.
        self.inlines = list(self.inlines)
        self.inlines.append(inline_admin)
        inline_instance = inline_admin(self.model, self.admin_site)
        self.content_inline_instances.append((content_cls, inline_instance))
        self.inline_instances.append(inline_instance)
        # Register with reversion.
        self._autoregister(inline, follow=["page"])
    
    def queryset(self, request):
        """Only allows editing of pages in this site."""
        return request.pages.all
                
    # Reversion

    def get_revision_form_data(self, request, obj, version):
        """
        Returns a dictionary of data to set in the admin form in order to revert
        to the given revision.
        """
        data = super(PageAdmin, self).get_revision_form_data(request, obj, version)
        content_version = version.revision.version_set.all().get(
            content_type = obj.content_type_id,
            object_id_int = obj.pk,
        )
        data.update(content_version.field_dict)
        return data

    # Plugable content types.

    def get_page_content_cls(self, request, obj=None):
        """Retrieves the page content type slug."""
        if PAGE_TYPE_PARAMETER in request.GET:
            return ContentType.objects.get_for_id(request.GET[PAGE_TYPE_PARAMETER]).model_class()
        if obj and obj.content_type:
            return obj.content_type.model_class()
        raise Http404, "You must specify a page content type."

    def get_fieldsets(self, request, obj=None):
        """Generates the custom content fieldsets."""
        content_cls = self.get_page_content_cls(request, obj)
        content_fields = [field.name for field in content_cls._meta.fields if field.name != "page"]
        fieldsets = super(PageAdmin, self).get_fieldsets(request, obj)
        if content_fields:
            content_fieldsets = content_cls.fieldsets or (
                ("Page content", {
                    "fields": content_fields,
                }),
            )
            fieldsets = tuple(fieldsets[0:1]) + content_fieldsets + tuple(fieldsets[1:])
        return fieldsets

    def get_form(self, request, obj=None, **kwargs):
        """Adds the template area fields to the form."""
        content_cls = self.get_page_content_cls(request, obj)
        form_attrs = {}
        for field in content_cls._meta.fields:
            if field.name == "page":
                continue
            form_field = self.formfield_for_dbfield(field, request=request)
            # HACK: add in the initial value. No other way to pass this on.
            if obj:
                try:
                    form_field.initial = getattr(obj.content, field.name, "")
                except content_cls.DoesNotExist:
                    pass  # This means that we're in a reversion recovery, or something weird has happened to the databae.
            # Store the field.
            form_attrs[field.name] = form_field
        ContentForm = type("%sForm" % self.__class__.__name__, (forms.ModelForm,), form_attrs)
        defaults = {"form": ContentForm}
        defaults.update(kwargs)
        PageForm = super(PageAdmin, self).get_form(request, obj, **defaults)
        # HACK: Need to limit parents field based on object. This should be done in
        # formfield_for_foreignkey, but that method does not know about the object instance.
        if obj:
            invalid_parents = set(child.id for child in obj.all_children)
            invalid_parents.add(obj.id)
        else:
            invalid_parents = frozenset()
        homepage = request.pages.homepage
        if homepage:
            parent_choices = []
            for page in [homepage] + homepage.all_children:
                if not page.id in invalid_parents:
                    parent_choices.append((page.id, u" \u203a ".join(unicode(breadcrumb) for breadcrumb in page.breadcrumbs)))
        else:
            parent_choices = []
        if not parent_choices:
            parent_choices = (("", "---------"),)
        PageForm.base_fields["parent"].choices = parent_choices
        # Return the completed form.
        return PageForm

    def save_model(self, request, obj, form, change):
        """Saves the model and adds its content fields."""
        content_cls = self.get_page_content_cls(request, obj)
        with locked(Page, content_cls, ContentType, HistoryLink):
            content_cls_type = ContentType.objects.get_for_model(content_cls)
            # Delete the old page content, if it's expired.
            if change and ContentType.objects.get_for_id(obj.content_type_id) != content_cls_type:
                obj.content.delete()
            # Create the page content.
            obj.content_type = content_cls_type
            if change:
                try:
                    content_obj = content_cls_type.model_class().objects.get(page=obj)
                except content_cls.DoesNotExist:
                    content_obj = content_cls()  # We're either in a reversion recovery, or something has gone very wrong with the database...
            else:
                content_obj = content_cls()
            # Modify the page content.
            for field in content_obj._meta.fields:
                if field.name == "page":
                    continue
                setattr(content_obj, field.name, form.cleaned_data[field.name])
            # Get the page order.
            if not obj.order:
                try:
                    obj.order = self.model.objects.order_by("-order").values_list("order", flat=True)[0] + 1
                except IndexError:
                    obj.order = 1
            # Save the model.
            super(PageAdmin, self).save_model(request, obj, form, change)
            # Save the page content.
            content_obj.page = obj
            content_obj.save()
    
    # Permissions.
    
    def has_add_content_permission(self, request, model):
        """Checks whether the given user can edit the given content model."""
        opts = model._meta
        return request.user.has_perm("{0}.{1}".format(opts.app_label, opts.get_add_permission()))
    
    def has_add_permission(self, request):
        """Checks whether the user can edits pages and at least one content model."""
        if not super(PageAdmin, self).has_add_permission(request):
            return False
        for content_model in get_registered_content():
            if self.has_add_content_permission(request, content_model):
                return True
        return False
    
    def has_change_permission(self, request, obj=None):
        """Checks whether the user can edit the page and associated content model."""
        if not super(PageAdmin, self).has_change_permission(request, obj):
            return False
        if obj:
            content_model = ContentType.objects.get_for_id(obj.content_type_id).model_class()
            content_opts = content_model._meta
            return request.user.has_perm("{0}.{1}".format(
                content_opts.app_label,
                content_opts.get_change_permission(),
            ))
        return True
        
    def has_delete_permission(self, request, obj=None):
        """Checks whether the user can delete the page and associated content model."""
        if not super(PageAdmin, self).has_delete_permission(request, obj):
            return False
        if obj:
            content_model = ContentType.objects.get_for_id(obj.content_type_id).model_class()
            content_opts = content_model._meta
            return request.user.has_perm("{0}.{1}".format(
                content_opts.app_label,
                content_opts.get_delete_permission(),
            ))
        return True
    
    # Custom views.
    
    def patch_response_location(self, request, response):
        """Perpetuates the 'from' key in all redirect responses."""
        if isinstance(response, HttpResponseRedirect):
            if PAGE_FROM_KEY in request.GET:
                response["Location"] += "?%s=%s" % (PAGE_FROM_KEY, request.GET[PAGE_FROM_KEY])
        return response
    
    def patch_inlines(self, request, obj, func):
        """Updates the admin inlines to only display those relevant to the content class."""
        # HACK: Not thread-safe, only suitable for process-based hosting.
        def do_patch_inlines(*args, **kwargs):
            with page_inlines_lock:
                inlines = self.inlines
                inline_instances = self.inline_instances
                try:
                    content_cls = self.get_page_content_cls(request, obj)
                    content_inline_instances = [
                        content_inline_instance
                        for content_inline_cls, content_inline_instance
                        in self.content_inline_instances
                        if content_inline_cls == content_cls
                    ]
                    # Trim current inline instances.
                    self.inlines = inlines[:-len(self.content_inline_instances)]
                    self.inline_instances = inline_instances[:-len(self.content_inline_instances)]
                    # Add in new ones.
                    for content_inline_instance in content_inline_instances:
                        self.inlines.append(content_inline_instance.__class__)
                        self.inline_instances.append(content_inline_instance)
                    # Run the func.
                    return func(*args, **kwargs)
                finally:
                    self.inlines = inlines
                    self.inline_instances = inline_instances
        return do_patch_inlines
            
    def changelist_view(self, request, *args, **kwargs):
        """Redirects to the sitemap, if appropriate."""
        if PAGE_FROM_KEY in request.GET:
            redirect_slug = request.GET[PAGE_FROM_KEY]
            if redirect_slug == PAGE_FROM_SITEMAP_VALUE:
                return redirect("admin:index")
        return super(PageAdmin, self).changelist_view(request, *args, **kwargs)
    
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
            context = {
                "title": "Select page type",
                "content_types": content_types
            }
            return render(request, "admin/pages/page/select_page_type.html", context)
        else:
            if not self.has_add_content_permission(request, ContentType.objects.get_for_id(request.GET[PAGE_TYPE_PARAMETER]).model_class()):
                raise PermissionDenied, "You are not allowed to add pages of that content type."
        return self.patch_inlines(request, None, super(PageAdmin, self).add_view)(request, *args, **kwargs)
    
    def change_view(self, request, object_id, *args, **kwargs):
        """Uses only the correct inlines for the page."""
        page = Page.objects.get(id=object_id)
        return self.patch_inlines(request, page, super(PageAdmin, self).change_view)(request, object_id, *args, **kwargs)
    
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

page_admin = site._registry[Page]