"""Admin settings for the static media management application."""


import os
from functools import partial

from django import template
from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.admin.views.main import IS_POPUP_VAR
from django.shortcuts import render_to_response
from django.template.defaultfilters import filesizeformat
from django.utils.text import truncate_words

from reversion.admin import VersionAdmin

from cms.apps.pages.admin import site
from cms.apps.media.models import Folder, File
from cms.apps.utils import thumbnails, permalinks


class FolderAdmin(admin.ModelAdmin):
    
    """Admin settings for Folder models."""
    
    list_display = ("name",)
    
    search_fields = ("name",)
    
    
site.register(Folder, FolderAdmin)
    
       
# Different types of file.
AUDIO_FILE = ("Audio", settings.CMS_MEDIA_URL + "img/file-types/audio-x-generic.png")
DOCUMENT_FILE = ("Document", settings.CMS_MEDIA_URL + "img/file-types/x-office-document.png")
SPREADSHEET_FILE = ("Spreadsheet", settings.CMS_MEDIA_URL + "img/file-types/x-office-spreadsheet.png")
TEXT_FILE = ("Plain text", settings.CMS_MEDIA_URL + "img/file-types/text-x-generic.png")
IMAGE_FILE = ("Image", settings.CMS_MEDIA_URL + "img/file-types/image-x-generic.png")
MOVIE_FILE = ("Movie", settings.CMS_MEDIA_URL + "img/file-types/video-x-generic.png")

# Different types of recognised file extensions.
FILE_TYPES = {"mp3": AUDIO_FILE,
              "wav": AUDIO_FILE,
              "doc": DOCUMENT_FILE,
              "odt": DOCUMENT_FILE,
              "pdf": DOCUMENT_FILE,
              "xls": SPREADSHEET_FILE,
              "txt": TEXT_FILE,
              "png": IMAGE_FILE,
              "gif": IMAGE_FILE,
              "jpg": IMAGE_FILE,
              "jpeg": IMAGE_FILE,
              "swf": MOVIE_FILE,
              "flv": MOVIE_FILE,
              "m4a": MOVIE_FILE,
              "mov": MOVIE_FILE,
              "wmv": MOVIE_FILE,}

UNKNOWN_FILE_ICON = settings.CMS_MEDIA_URL + "img/file-types/text-x-generic-template.png"
    
    
def get_file_type(filename):
    """Returns the file type tuple for the given filename."""
    name, extension = os.path.splitext(filename)
    if not extension:
        return ("", UNKNOWN_FILE_ICON)
    extension = extension.lower()[1:]
    if extension in FILE_TYPES:
        return FILE_TYPES[extension]
    return ("%s file" % extension.upper(), UNKNOWN_FILE_ICON)
        
    
class FileAdmin(VersionAdmin):
    
    """Admin settings for File models."""
    
    fieldsets = ((None, {"fields": ("title", "file",),},),
                 ("Media management", {"fields": ("folder",),},),)
    
    list_filter = ("folder",)
    
    search_fields = ("title",)
    
    list_display = ("get_preview", "get_title", "get_type", "get_size",)
    
    change_list_template = "admin/media/file/change_list.html"
    
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
    
    def get_preview(self, obj):
        """Generates a thumbnail of the image."""
        type = get_file_type(obj.file.name)
        permalink = permalinks.create(obj)
        if type == IMAGE_FILE:
            try:
                thumbnail = thumbnails.thumbnail(obj.file, 150, 100)
            except IOError:
                pass
            else:
                return '<img cms:permalink="%s" src="%s" width="%s" height="%s" alt="%s" title="%s"/>' % (permalink, thumbnail.url, thumbnail.width, thumbnail.height, obj.title, obj.title)
        return '<img cms:permalink="%s" src="%s" width="32" height="32" alt="%s" title="%s"/>' % (permalink, type[1], type[0], obj.title)
    get_preview.short_description = "preview"
    get_preview.allow_tags = True
    
    def get_title(self, obj):
        """Returns a truncated title of the object."""
        return truncate_words(obj.title, 8)
    get_title.short_description = "title"
    
    def get_type(self, obj):
        """Returns a pretty version of the file type."""
        return get_file_type(obj.file.name)[0]
    get_type.short_description = "type"
    
    # Custom views.
    
    def get_urls(self):
        """Enables custom admin views."""
        urls = super(FileAdmin, self).get_urls()
        custom_urls = patterns("",
                               url(r"^filebrowser.js$", self.admin_site.admin_view(self.filebrowser), name="media_file_filebrowser"))
        return custom_urls + urls
    
    def filebrowser(self, request):
        """Renders the javascript for the WYSIWYG file browser."""
        context = {}
        return render_to_response("admin/media/file/filebrowser.js", context, template.RequestContext(request), mimetype="text/javascript")
    
    
site.register(File, FileAdmin)

