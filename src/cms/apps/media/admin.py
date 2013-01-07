"""Admin settings for the static media management application."""

import os
from functools import partial

from django.contrib import admin
from django.contrib.admin.views.main import IS_POPUP_VAR
from django.shortcuts import render
from django.template.defaultfilters import filesizeformat
from django.utils.text import Truncator

import optimizations

from cms import permalinks, externals
from cms.apps.media.models import Label, File


class LabelAdmin(admin.ModelAdmin):
    
    """Admin settings for Label models."""
    
    list_display = ("name",)
    
    search_fields = ("name",)
    
    
admin.site.register(Label, LabelAdmin)
    
       
# Different types of file.
AUDIO_FILE_ICON = "media/img/audio-x-generic.png"
DOCUMENT_FILE_ICON = "media/img/x-office-document.png"
SPREADSHEET_FILE_ICON = "media/img/x-office-spreadsheet.png"
TEXT_FILE_ICON = "media/img/text-x-generic.png"
IMAGE_FILE_ICON = "media/img/image-x-generic.png"
MOVIE_FILE_ICON = "media/img/video-x-generic.png"
UNKNOWN_FILE_ICON = "media/img/text-x-generic-template.png"

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
    
    
class FileAdminBase(admin.ModelAdmin):
    
    """Admin settings for File models."""
    
    fieldsets = (
        (None, {
            "fields": ("title", "file",),
        },),
        ("Media management", {
            "fields": ("labels",),
            "classes": ("collapse",),
        },),
    )
    
    list_filter = ("labels",)
    
    search_fields = ("title",)
    
    list_display = ("get_preview", "get_title", "get_size",)

    change_list_template = "admin/media/file/change_list.html"
    
    filter_horizontal = ("labels",)
    
    # Customizations.
    
    def lookup_allowed(self, lookup, *args, **kwargs):
        """Allows the file iregex lookup needed by TinyMCE integration."""
        if lookup == "file__iregex":
            return True
        return super(FileAdminBase, self).lookup_allowed(lookup, *args, **kwargs)
    
    # Custom actions.
    
    def add_label_action(self, request, queryset, label):
        """Adds the label on the given queryset."""
        for file in queryset:
            file.labels.add(label)
            
    def remove_label_action(self, request, queryset, label):
        """Removes the label on the given queryset."""
        for file in queryset:
            file.labels.remove(label)
    
    def get_actions(self, request):
        """Generates the actions for assigning categories."""
        if IS_POPUP_VAR in request.GET:
            return []
        opts = self.model._meta
        verbose_name_plural = opts.verbose_name_plural
        actions = super(FileAdminBase, self).get_actions(request)
        # Add the dynamic labels.
        for label in Label.objects.all():
            # Add action.
            action_function = partial(self.__class__.add_label_action, label=label)
            action_description = u'Remove label %s from selected %s"' % (label.name, verbose_name_plural)
            action_name = action_description.lower().replace(" ", "_")
            actions[action_name] = (action_function, action_name, action_description)
            # Remove action.
            action_function = partial(self.__class__.remove_label_action, label=label)
            action_description = u'Remove label %s from selected %s"' % (label.name, verbose_name_plural)
            action_name = action_description.lower().replace(" ", "_")
            actions[action_name] = (action_function, action_name, action_description)
        return actions
    
    def remove_label(self, request, queryset):
        """Removes the label from selected files."""
        queryset.update(label=None)
    
    # Custom display routines.
    
    def get_label(self, obj):
        """Returns a pretty version of the label."""
        if obj.label:
            return obj.label.name
        return ""
    get_label.short_description = "label"
    get_label.admin_order_field = "label"
    
    def get_size(self, obj):
        """Returns the size of the media in a human-readable format."""
        try:
            return filesizeformat(obj.file.size)
        except OSError:
            return "0 bytes"
    get_size.short_description = "size"
    
    def get_preview(self, obj):
        """Generates a thumbnail of the image."""
        _, extension = os.path.splitext(obj.file.name)
        extension = extension.lower()[1:]
        icon = FILE_ICONS.get(extension, UNKNOWN_FILE_ICON)
        permalink = permalinks.create(obj)
        if icon == IMAGE_FILE_ICON:
            try:
                thumbnail = optimizations.get_thumbnail(obj.file, 100, 66)
            except IOError:
                pass
            else:
                return '<img cms:permalink="%s" src="%s" width="%s" height="%s" alt="" title="%s"/>' % (permalink, thumbnail.url, thumbnail.width, thumbnail.height, obj.title)
        else:
            icon = optimizations.get_url(icon)
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
        return super(FileAdminBase, self).response_add(request, obj, *args, **kwargs)
    
    def changelist_view(self, request, extra_context=None):
        """Renders the change list."""
        context = {
            "changelist_template_parent": externals.reversion and "reversion/change_list.html" or "admin/change_list.html",
        }
        if extra_context:
            context.update(extra_context)
        return super(FileAdminBase, self).changelist_view(request, context)


# Renaming needed to allow inheritance to take place in this class without infinite recursion.
FileAdmin = FileAdminBase


if externals.reversion:
    class FileAdmin(FileAdmin, externals.reversion["admin.VersionMetaAdmin"]):
        list_display = FileAdmin.list_display + ("get_date_modified",)
    
    
if externals.watson:
    class FileAdmin(FileAdmin, externals.watson["admin.SearchAdmin"]):
        pass
        
    
admin.site.register(File, FileAdmin)
