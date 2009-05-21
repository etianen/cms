"""Admin settings for the page management application."""


from django import forms
from django.forms.models import ModelFormMetaclass, media_property
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
        template_area_fields = ["%s_content" % area for area in template_areas]
        return template_area_fields
    
    def get_form(self, request, obj=None, **kwargs):
        """Adds the template area fields to the form."""
        if obj:
            initial = [content.content for content in obj.content_set.all()]
        else:
            initial = ["" for field in self.get_template_area_fields()]
        form_attrs = dict([(template_area_field, forms.CharField(label=template_area_field.rsplit("_", 1)[0].replace("_", " ").capitalize(),
                                                                 initial=initial[index],
                                                                 required=False,
                                                                 widget=HtmlWidget))
                           for index, template_area_field
                           in enumerate(self.get_template_area_fields())])
        Form = type("%sForm" % self.model.__name__, (forms.ModelForm,), form_attrs)
        defaults = {"form": Form}
        defaults.update(kwargs)
        return super(PageAdmin, self).get_form(request, obj, **defaults)
    
    def get_fieldsets(self, request, obj=None):
        """Generates the custom content fieldsets."""
        fieldsets = super(PageAdmin, self).get_fieldsets(request, obj)
        template_area_fields = self.get_template_area_fields()
        content_fieldset = ("Page content", {"fields": template_area_fields})
        fieldsets = (fieldsets[0], content_fieldset) + fieldsets[1:]
        return fieldsets
    
    def save_model(self, request, obj, form, change):
        """Saves the model and adds its content fields."""
        obj.save()
        content_set = obj.content_set.all()
        for index, template_area_field in enumerate(self.get_template_area_fields()):
            template_area_content = form.cleaned_data[template_area_field]
            try:
                content = content_set[index]
            except IndexError:
                content = Content()
                content.page = obj
            content.content = template_area_content
            content.save()

    
site.register(Page, PageAdmin)

