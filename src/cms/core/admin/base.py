"""Base classes for the CMS admin interface."""


from django.conf import settings
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils import dateformat 

from reversion.admin import VersionAdmin


class PublishedModelAdmin(admin.ModelAdmin):
    
    """Base admin class for published models."""
    
    actions = ("publish_selected", "unpublish_selected",)
    
    change_form_template = "admin/core/publishedmodel/change_form.html"
    
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


def get_date_modified(admin, obj, field_name="date_modified"):
    """Returns the date modified timestamp and the user who did the deed."""
    try:
        datestr = dateformat.format(getattr(obj, field_name), settings.DATE_FORMAT)
        try:
            latest_log = LogEntry.objects.select_related().filter(object_id=obj.pk, content_type=ContentType.objects.get_for_model(obj)).order_by("-action_time")[0]
        except IndexError:
            userstr = ""
        else:
            user = latest_log.user
            if user.first_name and user.last_name:
                userstr = "by %s %s" % (user.first_name, user.last_name)
            else:
                userstr = "by %s" % user.username
        return " ".join((datestr, userstr))
    except Exception, ex:
        print ex
get_date_modified.admin_order_field = "date_modified"
get_date_modified.short_description = "last modified"


class PageBaseAdmin(VersionAdmin, PublishedModelAdmin):
    
    """Base admin class for ArticleBase models."""
    
    base_fieldsets = ((None, {"fields": ("title", "url_title",),},),)
    
    navigation_fieldsets = (("Navigation", {"fields": ("short_title",),
                                            "classes": ("collapse",),}),)
    
    seo_fieldsets = (("Search engine optimization", {"fields": ("browser_title", "meta_keywords", "meta_description", "robots_index", "robots_follow", "robots_archive", "sitemap_priority", "sitemap_changefreq",),
                                                     "classes": ("collapse",),},),)
    
    fieldsets = base_fieldsets + PublishedModelAdmin.publication_fieldsets + navigation_fieldsets + seo_fieldsets

    list_display = ("title", "is_online", "get_date_modified",)
    
    prepopulated_fields = {"url_title": ("title",),}
    
    search_fields = ("title",)
    
    get_date_modified = get_date_modified