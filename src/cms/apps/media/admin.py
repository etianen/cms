"""Admin settings for the static media management application."""


import os

from django import template
from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.shortcuts import render_to_response
from django.template.defaultfilters import filesizeformat

from cms.apps.pages import thumbnails
from cms.apps.pages.admin import site
from cms.lib.media.models import Folder, File, Image


class FolderAdmin(admin.ModelAdmin):
    
    """Admin settings for Folder models."""
    
    list_display = ("name",)
    
    search_fields = ("name",)
    
    
site.register(Folder, FolderAdmin)


class MediaAdmin(admin.ModelAdmin):
    
    """Base admin settings for Media models."""
    
    date_hierarchy = "last_modified"
    
    fieldsets = ((None, {"fields": ("title", "file",),},),
                 ("Media management", {"fields": ("folder", "keywords", "notes",),},),)
    
    list_display = ("title", "get_folder", "get_size", "last_modified", "notes",)
    
    list_filter = ("folder",)
    
    list_select_related = True
    
    search_fields = ("name", "keywords",)
    
    # Custom actions.
    
    def get_actions(self, request):
        """Generates the actions for assigning categories."""
        opts = self.model._meta
        verbose_name_plural = opts.verbose_name_plural
        actions = super(MediaAdmin, self).get_actions(request)
        # Add the dynamic folders.
        for folder in Folder.objects.all():
            action_function = lambda model_admin, request, queryset: queryset.update(folder=folder)
            action_description = u'Move selected %s to "%s"' % (verbose_name_plural, folder.name)
            action_name = action_description.lower().replace(" ", "_")
            actions[action_name] = (action_function, action_name, action_description)
        # Add the remove folder action.
        remove_folder_function = self.__class__.remove_folder
        remove_folder_description = u"Remove selected %s from folder" % verbose_name_plural
        remove_folder_name = "folder"
        actions[remove_folder_name] = (remove_folder_function, remove_folder_name, remove_folder_description)
        return actions
    
    def remove_folder(self, request, queryset):
        """Removes the folder from selected files."""
        queryset.update(folder=None)
    
    # Custom display routines.
    
    def get_folder(self, obj):
        """Returns a pretty version of the folder."""
        if obj.folder:
            return obj.folder.name
        return ""
    get_folder.short_description = "folder"
    get_folder.admin_order_field = "folder"
    
    def get_size(self, obj):
        """Returns the size of the media in a human-readable format."""
        return filesizeformat(obj.size)
    get_size.short_description = "size"
    get_size.admin_order_field = "size"
    
    
# Convert the tuples into a dict for faster lookup.
FILE_TYPES = dict(settings.FILE_TYPES)
    
    
class FileAdmin(MediaAdmin):
    
    """Admin settings for File models."""
    
    list_display = ("title", "get_type", "get_folder", "get_size", "last_modified", "notes",)
    
    # Custom display routines.
    
    def get_type(self, obj):
        """Returns a pretty version of the file type."""
        # Split the extension off the file name.
        name, extension = os.path.splitext(obj.file.name)
        if not extension:
            return ""
        # Remove the leading dot and standardize to lowercase.
        extension = extension.lower()[1:]
        if extension in FILE_TYPES:
            return FILE_TYPES[extension]
        return "%s file" % extension.upper()
    get_type.short_description = "type"
    
    # Custom admin views.
    
    def get_urls(self):
        """Creates custom admin URLs for File models."""
        urlpatterns = super(FileAdmin, self).get_urls()
        urlpatterns += patterns("", url(r"^link-list.js$", self.admin_site.admin_view(self.link_list), name="admin_media_file_link_list"))
        return urlpatterns
    
    def link_list(self, request):
        """Returns a list of TinyMCE links."""
        files = self.queryset(request)
        context = {"files": files}
        return render_to_response("admin/media/file/link_list.js", context, template.RequestContext(request), mimetype="text/javascript")
    
    
site.register(File, FileAdmin)


class ImageAdmin(MediaAdmin):
    
    """Admin settings for Image models."""
    
    list_display = ("get_thumbnail", "title", "get_folder", "width", "height", "get_size", "last_modified", "notes",)
    
    # Custom display routines.
    
    def get_thumbnail(self, obj):
        """Generates a thumbnail of the image."""
        thumbnail = thumbnails.thumbnail(obj.file, 150, 100)
        return '<img src="%s" width="%s" height="%s" alt=""/>' % (thumbnail.url, thumbnail.width, thumbnail.height)
        
    get_thumbnail.short_description = "thumbnail"
    get_thumbnail.allow_tags = True
    
    # Custom admin views.
    
    def get_urls(self):
        """Creates custom admin URLs for File models."""
        urlpatterns = super(ImageAdmin, self).get_urls()
        urlpatterns += patterns("", url(r"^image-list.js$", self.admin_site.admin_view(self.image_list), name="admin_media_image_image_list"))
        return urlpatterns
    
    def image_list(self, request):
        """Returns a list of TinyMCE images."""
        images = self.queryset(request)
        context = {"image": images}
        return render_to_response("admin/media/image/image_list.js", context, template.RequestContext(request), mimetype="text/javascript")
    
    
site.register(Image, ImageAdmin)

