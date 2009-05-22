"""Admin settings for the page management application."""


from django import forms
from django.forms.models import ModelFormMetaclass, media_property
from django.contrib import admin
from django.db import models
from django.http import Http404

from cms.core.admin import ContentAdmin, site
from cms.core.widgets import HtmlWidget
from cms.pages.models import Page, get_page_content_type


class PageAdmin(ContentAdmin):
    
    """Admin settings for Page models."""
    
    fieldsets = ((None, {"fields": ("title", "url_title", "parent", "is_online",),},),
                 ("Publication", {"fields": ("publication_date", "expiry_date",),
                                  "classes": ("collapse",)}),
                 ("Navigation", {"fields": ("short_title", "in_navigation",),
                                 "classes": ("collapse",),},),) + ContentAdmin.seo_fieldsets

    prepopulated_fields = {"url_title": ("title",),}
    
    def get_page_content(self, request, obj=None):
        """Retrieves the page content object."""
        # Try to use an instance.
        if obj:
            return obj.content
        # Create an unbound page content.
        try:
            page_content_name = request.GET["type"]
        except KeyError: 
            raise Http404, "You must specify a page content type."
        try:
            page_content_cls = get_page_content_type(page_content_name)
        except KeyError:
            raise Http404, "%r is not a valid page content type." % page_content_name
        page_content = page_content_cls(page_content_name, None, {})
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
        if change:
            page_content = self.get_page_content(request, obj)
        else:
            page_content = self.get_page_content(request, None)
        for field_name in page_content.get_field_names():
            field_data = form.cleaned_data[field_name]
            setattr(page_content, field_name, field_data)
        obj.content = page_content
        obj.save()

    
site.register(Page, PageAdmin)

