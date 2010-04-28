"""
The upgraded CMS online admin area.

This is an enhanced version of the Django admin area, providing a more
user-friendly appearance and providing additional functionality over the
standard implementation.
"""

from __future__ import with_statement

import functools, itertools

from django import template
from django.conf.urls.defaults import patterns, url
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response
from django.views.generic.simple import direct_to_template
from django.utils import dateformat 

from reversion.admin import VersionAdmin

from cms.core import permalinks
from cms.core.models.managers import publication_manager


class AdminSite(admin.AdminSite):
    
    """The CMS admin site."""
    
    index_template = "admin/dashboard.html"
    
    def __init__(self, *args, **kwargs):
        """Initializes the admin site."""
        super(AdminSite, self).__init__(*args, **kwargs)
        self._link_list_models = set()
    
    def register_link_list(self, model):
        """Registers a model in the admin tinymce link list generator."""
        self._link_list_models.add(model)
        
    def unregister_link_list(self, model):
        """Removes a model from the admin tinymce link list generator."""
        self._link_list_models.remove(model)
    
    # Custom admin views.
    
    def get_urls(self):
        """Generates custom admin URLS."""
        urls = super(AdminSite, self).get_urls()
        custom_urls = patterns("",
                               url(r"^tinymce-init.js$", self.admin_view(direct_to_template), kwargs={"template": "admin/tinymce_init.js", "mimetype": "text/javascript"}, name="tinymce_init"),
                               url(r"^tinymce-link-list.js$", self.admin_view(self.tinymce_link_list), name="tinymce_link_list"),)
        return custom_urls + urls
    
    def admin_view(self, view, *args, **kwargs):
        """Turns off publication management for admin views."""
        view = super(AdminSite, self).admin_view(view, *args, **kwargs)
        @functools.wraps(view)
        def wrapper(*args, **kwargs):
            with publication_manager.select_published(False):
                return view(*args, **kwargs)
        return wrapper
    
    def tinymce_link_list(self, request):
        """Generates the tinymce link list."""
        generators = []
        for model in self._link_list_models:
            generators.append((unicode(obj), permalinks.create(obj)) for obj in model._default_manager.all().iterator())
        links = sorted(itertools.chain(*generators))
        context = {"links": links}
        return render_to_response("admin/tinymce_link_list.js", context, template.RequestContext(request), mimetype="text/javascript")
        
    
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
    
    ordering = ("title",)
    
    get_date_modified = get_date_modified