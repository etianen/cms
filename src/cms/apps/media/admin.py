"""Admin settings for the static media management application."""


import os
from functools import partial

from django.conf.urls.defaults import patterns
from django.contrib import admin
from django.contrib.admin.views.main import IS_POPUP_VAR
from django.template.defaultfilters import filesizeformat
from django.utils.text import truncate_words

from reversion.admin import VersionAdmin

from cms.apps.pages.admin import site
from cms.apps.media.models import Folder, File, Image
from cms.apps.utils import thumbnails, permalinks


class FolderAdmin(admin.ModelAdmin):
    
    """Admin settings for Folder models."""
    
    list_display = ("name",)
    
    search_fields = ("name",)
    
    
site.register(Folder, FolderAdmin)


class MediaAdmin(VersionAdmin):
    
    """Base admin settings for Media models."""
    
    fieldsets = ((None, {"fields": ("title", "file",),},),
                 ("Media management", {"fields": ("folder",),},),)
    
    list_filter = ("folder",)
    
    search_fields = ("title",)
    
    # Custom actions.
    
    def update_folder_action(self, request, queryset, folder):
        """Updates the folder on the given queryset."""
        queryset.update(folder=folder)
    
    def get_actions(self, request):
        """Generates the actions for assigning categories."""
        if IS_POPUP_VAR in request.GET:
            return []
        opts = self.model._meta
        verbose_name_plural = opts.verbose_name_plural
        actions = super(MediaAdmin, self).get_actions(request)
        # Add the dynamic folders.
        for folder in Folder.objects.all():
            action_function = partial(self.__class__.update_folder_action, folder=folder)
            action_description = u'Move selected %s to folder "%s"' % (verbose_name_plural, folder.name)
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
        try:
            return filesizeformat(obj.file.size)
        except OSError:
            return "0 bytes"
    get_size.short_description = "size"
    
       
# Different types of recognised file extensions.
FILE_TYPES = {"mp3": "Audio",
              "wav": "Audio",
              "doc": "Document",
              "odt": "Document",
              "pdf": "Document",
              "xls": "Spreadsheet",
              "txt": "Plain text",
              "png": "Image",
              "gif": "Image",
              "jpg": "Image",
              "jpeg": "Image",
              "swf": "Movie",
              "flv": "Movie",
              "m4a": "Movie",
              "mov": "Movie",
              "wmv": "Movie",}
    
    
class FileAdmin(MediaAdmin):
    
    """Admin settings for File models."""
    
    list_display = ("get_thumbnail", "get_title", "get_type", "get_size",)
    
    change_list_template = "admin/media/file/change_list.html"
    
    # Custom display routines.
    
    def get_thumbnail(self, obj):
        """Generates a thumbnail of the image."""
        thumbnail = thumbnails.thumbnail(obj.file, 150, 100)
        return '<img src="%s" width="%s" height="%s" alt=""/>' % (thumbnail.url, thumbnail.width, thumbnail.height)
    get_thumbnail.short_description = "thumbnail"
    get_thumbnail.allow_tags = True
    
    def get_title(self, obj):
        """Returns a truncated title of the object."""
        return truncate_words(obj.title, 8)
    get_title.short_description = "title"
    
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
    
    # Custom views.
    
    def get_urls(self):
        """Enables custom admin views."""
        urls = super(FileAdmin, self).get_urls()
        custom_urls = patterns('',)
        return custom_urls + urls
    
    
site.register(File, FileAdmin)


class ImageAdmin(MediaAdmin):
    
    """Admin settings for Image models."""
    
    list_display = ("get_thumbnail", "title", "get_folder", "width", "height", "get_size", "last_modified",)
    
    # Custom display routines.
    
    def get_thumbnail(self, obj):
        """Generates a thumbnail of the image."""
        thumbnail = thumbnails.thumbnail(obj.file, 150, 100)
        return '<img src="%s" width="%s" height="%s" alt=""/>' % (thumbnail.url, thumbnail.width, thumbnail.height)
    get_thumbnail.short_description = "thumbnail"
    get_thumbnail.allow_tags = True
    
    # Custom views.
    
    def get_urls(self):
        """Enables custom admin views."""
        urls = super(ImageAdmin, self).get_urls()
        custom_urls = patterns('',)
        return custom_urls + urls
    
    
site.register(Image, ImageAdmin)

