"""Admin settings for the staff management application."""


from django import template
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import redirect, render_to_response

from cms.core.admin import site
from cms.lib.staff.forms import UserCreationForm
from cms.lib.staff.models import User, Group, Permission


GROUPS_DESCRIPTION = '<p class="help"><strong>Administrators</strong> can create users and edit site content. <strong>Editors</strong> may only edit site content.</p>'


class UserAdmin(BaseUserAdmin):
    
    """Admin settings for User models."""
    
    actions = ("activate_selected", "deactivate_selected",)
    
    add_form = UserCreationForm
    
    fieldsets = ((None, {"fields": ("username", "is_active",)}),
                 ("Personal information", {"fields": ("first_name", "last_name", "email",)}),
                 ("Groups", {"fields": ("groups",),
                             "description": GROUPS_DESCRIPTION}),)
    
    filter_horizontal = ("user_permissions", "groups",)
    
    list_display = ("username", "first_name", "last_name", "email", "is_active",)
    
    list_filter = ("is_active",)
    
    # Custom admin actions.
    
    def activate_selected(self, request, queryset):
        """Activates the selected user accounts."""
        queryset.update(is_active=True)
    activate_selected.short_description = "Activate selected users"
    
    def deactivate_selected(self, request, queryset):
        """Deactivates the selected user accounts."""
        queryset.update(is_active=False)
    deactivate_selected.short_description = "Deactivate selected users"
    
    # Custom admin views.
    
    def add_view(self, request):
        """Allows new users to be added to the admin interface."""
        if request.method == "POST":
            form = self.add_form(request.POST)
            if form.is_valid():
                new_user = form.save()
                message = 'The user "%s" was added successfully.' % new_user
                self.log_addition(request, new_user)
                if "_addanother" in request.POST:
                    self.message_user(request, message)
                    return redirect("admin_staff_user_add")
                elif "_popup" in request.REQUEST:
                    return self.response_add(request, new_user)
                elif "_continue" in request.POST:
                    message = message + " You may edit it again below."
                    self.message_user(request, message)
                    return redirect("admin_staff_user_change", new_user.id)
                else:
                    self.message_user(request, message)
                    return redirect("admin_staff_user_changelist")
        else:
            form = self.add_form()
        media = self.media + form.media
        context = {"title": "Add user",
                   "form": form,
                   "is_popup": "_popup" in request.REQUEST,
                   "add": True,
                   "change": False,
                   "has_add_permission": self.has_add_permission(request),
                   "has_delete_permission": False,
                   "has_change_permission": self.has_change_permission(request),
                   "has_file_field": False,
                   "has_absolute_url": False,
                   "auto_populated_fields": (),
                   "opts": self.model._meta,
                   "media": media,
                   "save_as": False,
                   "root_path": self.admin_site.root_path,
                   "app_label": self.model._meta.app_label,
                   "groups_description": GROUPS_DESCRIPTION}
        return render_to_response("admin/staff/user/add_form.html", context, template.RequestContext(request))
    
    
site.register(User, UserAdmin)


class GroupAdmin(admin.ModelAdmin):
    
    """Admin settings for Group models."""
    
    filter_horizontal = ('permissions',)
    
    list_display = ("name",)
    
    search_fields = ("name",)
    
    ordering = ("name",)
    
    # FIXME: Proxy models return the content type of their parent model when
    # get_for_model is used.
    # FIXME: No permissions are created for proxy models.
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Sets up custom foreign key choices."""
        if db_field.name == "permissions":
            content_types = [ContentType.objects.get_for_model(model)
                             for model in self.admin_site._registry.keys()]
            permissions = Permission.objects.filter(content_type__in=content_types)
            permissions = permissions.order_by("content_type__app_label", "content_type__model", "name")
            kwargs["queryset"] = permissions
        return super(GroupAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    
site.register(Group, GroupAdmin)

