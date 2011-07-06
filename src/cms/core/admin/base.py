"""Base classes for the CMS admin interface."""

from django.conf import settings
from django.contrib import admin
from django.utils import dateformat 

from reversion.admin import VersionAdmin


class AuditBaseAdmin(admin.ModelAdmin):
    
    """Base class for audited models."""
    
    list_display = ("__unicode__", "get_last_modified",)
    
    def get_last_modified(self, obj):
        """Returns the date modified timestamp and the user who did the deed."""
        datestr = dateformat.format(obj.date_modified, settings.DATE_FORMAT)
        if obj.last_modified_user:
            user = obj.last_modified_user
            if user.first_name and user.last_name:
                userstr = u"by {first_name} {last_name}".format(
                    first_name = user.first_name,
                    last_name = user.last_name,
                )
            else:
                userstr = u"by {username}".format(
                    username = user.username
                )
        else:
            userstr = ""
        return u" ".join((datestr, userstr))
    get_last_modified.admin_order_field = "date_modified"
    get_last_modified.short_description = "last modified"
    
    def save_model(self, request, obj, form, change):
        """Saves the model, attaching the user model."""
        obj.save(user=request.user)
            

class PublishedBaseAdmin(AuditBaseAdmin):
    
    """Base admin class for published models."""
    
    list_display = ("__unicode__", "is_online", "get_last_modified",)
    
    actions = ("publish_selected", "unpublish_selected",)
    
    change_form_template = "admin/core/publishedmodel/change_form.html"
    
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


class EntityBaseAdmin(VersionAdmin, PublishedBaseAdmin):
    
    """Base admin class for EntityBase models."""


class PageBaseAdmin(EntityBaseAdmin):
    
    """Base admin class for PageBase models."""

    list_display = ("title", "is_online", "get_last_modified",)
    
    prepopulated_fields = {"url_title": ("title",),}
    
    search_fields = ("title",)