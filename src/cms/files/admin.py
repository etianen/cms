"""Admin settings for the file management application."""


from django import template
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.shortcuts import render_to_response
from django.template.defaultfilters import filesizeformat

from cms.core.admin import site
from cms.files.models import Category, File


class CategoryAdmin(admin.ModelAdmin):
    
    """Admin settings for Category models."""
    
    list_display = ("name",)
    
    search_fields = ("name",)
    
    
site.register(Category, CategoryAdmin)


class FileAdmin(admin.ModelAdmin):
    
    """Admin settings for File models."""
    
    list_display = ("title", "category", "size")
    
    list_filter = ("category",)
    
    search_fields = ("title",)
    
    # Custom actions.
    
    def get_actions(self, request):
        """Generates the actions for assigning categories."""
        actions = super(FileAdmin, self).get_actions(request)
        # Add the dynamic file categories.
        for category in Category.objects.all():
            action_function = lambda model_admin, request, queryset: queryset.update(category=category)
            action_description = "Move selected files to %s" % category.name
            action_name = action_description.lower().replace(" ", "_")
            actions[action_name] = (action_function, action_name, action_description)
        # Add the remove category action.
        remove_category_function = self.__class__.remove_category
        remove_category_description = "Remove selected files from category"
        remove_category_name = "remove_category"
        actions[remove_category_name] = (remove_category_function, remove_category_name, remove_category_description)
        return actions
    
    def remove_category(self, request, queryset):
        """Removes the category from selected files."""
        queryset.update(category=None)
    
    # Custom display routines.
    
    def size(self, obj):
        """Returns the size of the file in a human-readable format."""
        return filesizeformat(obj.file.size)
    
    # Custom views.
    
    def get_urls(self):
        """Adds some custom functionality to the file admin."""
        admin_view_wrapper = self.admin_site.admin_view
        urlpatterns = patterns("",
                               url(r"^tiny-mce-link-list.js$", admin_view_wrapper(self.tiny_mce_link_list), name="admin_files_file_tiny_mce_link_list"),)
        urlpatterns += super(FileAdmin, self).get_urls()
        return urlpatterns
    
    def tiny_mce_link_list(self, request):
        """Renders the TinyMCE link list."""
        files = self.queryset(request)
        context = {"files": files}
        return render_to_response("admin/files/file/tiny_mce_link_list.js", context, template.RequestContext(request), mimetype="text/javascript")
    

site.register(File, FileAdmin)

