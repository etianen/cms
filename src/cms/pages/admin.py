"""Admin settings for the page management application."""


from django import forms
from django.contrib import admin
from django.db import models

from cms.core.admin import ContentAdmin, site
from cms.core.widgets import HtmlWidget
from cms.pages.models import Page, Content


class PageAdmin(ContentAdmin):
    
    """Admin settings for Page models."""
    
    fieldsets = ((None, {"fields": ("title", "url_title", "parent", "is_online",),},),
                 ("Publication", {"fields": ("publication_date", "expiry_date",),
                                  "classes": ("collapse",)}),
                 ("Navigation", {"fields": ("short_title", "in_navigation",),
                                 "classes": ("collapse",),},),) + ContentAdmin.seo_fieldsets

    prepopulated_fields = {"url_title": ("title",),}
    
    def get_template_area_fields(self):
        """Returns the names of the template area fields."""
        template_areas = self.model.template_areas
        template_area_fields = ["content_%s" % area for area in template_areas]
        return template_area_fields
    
    def get_form(self, request, obj=None, **kwargs):
        """Adds the template area fields to the form."""
        BaseForm = super(PageAdmin, self).get_form(request, obj, **kwargs)
        form_attrs = dict([(template_area_field, forms.CharField(label=template_area_field.split("_", 1)[1].replace("_", " ").capitalize(),
                                                                 widget=HtmlWidget))
                           for template_area_field in self.get_template_area_fields()])
        Form = type("%sForm" % self.model.__name__, (BaseForm,), form_attrs)
        return Form
    
    def get_fieldsets(self, request, obj=None):
        """Generates the custom content fieldsets."""
        fieldsets = super(PageAdmin, self).get_fieldsets(request, obj)
        template_area_fields = self.get_template_area_fields()
        content_fieldset = ("Page content", {"fields": template_area_fields})
        fieldsets = (fieldsets[0], content_fieldset) + fieldsets[1:]
        return fieldsets

    
site.register(Page, PageAdmin)

