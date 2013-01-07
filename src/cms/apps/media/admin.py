"""Admin settings for the static media management application."""

import os
from functools import partial

from django.conf import settings
from django.contrib.admin.views.main import IS_POPUP_VAR
from django.shortcuts import render
from django.template.defaultfilters import filesizeformat
from django.utils.text import Truncator

from reversion.admin import VersionAdmin

from cms.core import thumbnails, permalinks
from cms.core.admin import AuditBaseAdmin, site
from cms.apps.media.models import Folder, File


class FolderAdmin(AuditBaseAdmin):
    
    """Admin settings for Folder models."""
    
    list_display = ("name", "get_last_modified",)
    
    search_fields = ("name",)
    
    
site.register(Folder, FolderAdmin)
    
       
# Different types of file.
AUDIO_FILE_ICON = settings.STATIC_URL + "cms/img/file-types/audio-x-generic.png"
DOCUMENT_FILE_ICON = settings.STATIC_URL + "cms/img/file-types/x-office-document.png"
SPREADSHEET_FILE_ICON = settings.STATIC_URL + "cms/img/file-types/x-office-spreadsheet.png"
TEXT_FILE_ICON = settings.STATIC_URL + "cms/img/file-types/text-x-generic.png"
IMAGE_FILE_ICON = settings.STATIC_URL + "cms/img/file-types/image-x-generic.png"
MOVIE_FILE_ICON = settings.STATIC_URL + "cms/img/file-types/video-x-generic.png"
UNKNOWN_FILE_ICON = settings.STATIC_URL + "cms/img/file-types/text-x-generic-template.png"

# Different types of recognised file extensions.
FILE_ICONS = {
    "mp3": AUDIO_FILE_ICON,
    "m4a": AUDIO_FILE_ICON,
    "wav": AUDIO_FILE_ICON,
    "doc": DOCUMENT_FILE_ICON,
    "odt": DOCUMENT_FILE_ICON,
    "pdf": DOCUMENT_FILE_ICON,
    "xls": SPREADSHEET_FILE_ICON,
    "txt": TEXT_FILE_ICON,
    "png": IMAGE_FILE_ICON,
    "gif": IMAGE_FILE_ICON,
    "jpg": IMAGE_FILE_ICON,
    "jpeg": IMAGE_FILE_ICON,
    "swf": MOVIE_FILE_ICON,
    "flv": MOVIE_FILE_ICON,
    "mp4": MOVIE_FILE_ICON,
    "mov": MOVIE_FILE_ICON,
    "wmv": MOVIE_FILE_ICON,
}
    
    
class FileAdmin(VersionAdmin, AuditBaseAdmin):
    
    """Admin settings for File models."""
    
    fieldsets = ((None, {"fields": ("title", "file",),},),
                 ("Media management", {"fields": ("folder",),},),)
    
    list_filter = ("folder",)
    
    search_fields = ("title",)
    
    list_display = ("get_preview", "get_title", "get_size", "get_last_modified")

    change_list_template = "admin/media/file/change_list.html"
    
    # Customizations.
    
    def lookup_allowed(self, lookup, *args, **kwargs):
        """Allows the file iregex lookup needed by TinyMCE integration."""
        if lookup == "file__iregex":
            return True
        return super(FileAdmin, self).lookup_allowed(lookup, *args, **kwargs)
    
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
        actions = super(FileAdmin, self).get_actions(request)
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
        _, extension = os.path.splitext(obj.file.name)  # @UnusedVariable
        extension = extension.lower()[1:]
        icon = FILE_ICONS.get(extension, UNKNOWN_FILE_ICON)
        permalink = permalinks.create(obj)
        if icon == IMAGE_FILE_ICON:
            try:
                thumbnail = thumbnails.create(obj.file, 100, 66)
            except IOError:
                pass
            else:
                return '<img cms:permalink="%s" src="%s" width="%s" height="%s" alt="" title="%s"/>' % (permalink, thumbnail.url, thumbnail.width, thumbnail.height, obj.title)
        return '<img cms:permalink="%s" src="%s" width="66" height="66" alt="" title="%s"/>' % (permalink, icon, obj.title)
    get_preview.short_description = "preview"
    get_preview.allow_tags = True
    
    def get_title(self, obj):
        """Returns a truncated title of the object."""
        return Truncator(obj.title).words(8)
    get_title.short_description = "title"
    
    # Custom view logic.
    
    def response_add(self, request, obj, *args, **kwargs):
        """Returns the response for a successful add action."""
        if "_tinymce" in request.GET:
            context = {"permalink": permalinks.create(obj),
                       "title": obj.title}
            return render(request, "admin/media/file/filebrowser_add_success.html", context)
        return super(FileAdmin, self).response_add(request, obj, *args, **kwargs)
    
    
site.register(File, FileAdmin)