"""Admin settings for the staff management application."""


from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.shortcuts import redirect, render_to_response

from cms.core.admin import site
from cms.staff.forms import UserCreationForm
from cms.staff.models import User, Group


class UserAdmin(BaseUserAdmin):
    
    """Admin settings for User models."""
    
    add_form = UserCreationForm
    
    fieldsets = ((None, {"fields": ("username", "is_active",)}),
                 ("Personal information", {"fields": ("first_name", "last_name", "email",)}),
                 ("Groups", {"fields": ("groups",)}),
                 ("Advanced permissions", {"fields": ("is_superuser", "user_permissions",),
                                  "classes": ("collapse",)}),)
    
    filter_horizontal = ("user_permissions", "groups",)
    
    list_display = ("username", "first_name", "last_name", "email", "is_active",)
    
    list_filter = ("is_active",)
    
    def add_view(self, request):
        """Allows new users to be added to the admin interface."""
        if request.method == 'POST':
            form = self.add_form(request.POST)
            if form.is_valid():
                new_user = form.save()
                message = 'The user "%s" was added successfully.' % new_user
                self.log_addition(request, new_user)
                if "_addanother" in request.POST:
                    request.user.message_set.create(message=message)
                    return redirect("admin_auth_user_add")
                elif "_popup" in request.REQUEST:
                    return self.response_add(request, new_user)
                elif "_continue" in request.POST:
                    message = message + " You may edit it again below."
                    request.user.message_set.create(message=message)
                    return redirect("admin_auth_user_change", new_user.id)
                else:
                    request.user.message_set.create(message=message)
                    return redirect("admin_auth_user_changelist")
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
                   "app_label": self.model._meta.app_label,}
        return render_to_response("admin/auth/user/add_form.html", context, template.RequestContext(request))
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Sets up custom foreign key choices."""
        if db_field.name == "user_permissions":
            kwargs["queryset"] = self.admin_site.get_permissions(request)
        return super(UserAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)
    
    def queryset(self, request):
        """Only displays staff users."""
        queryset = super(UserAdmin, self).queryset(request)
        queryset = queryset.filter(is_staff=True)
        return queryset
    
    
site.register(User, UserAdmin)


class GroupAdmin(admin.ModelAdmin):
    
    """Admin settings for Group models."""
    
    filter_horizontal = ('permissions',)
    
    list_display = ("name",)
    
    search_fields = ("name",)
    
    ordering = ("name",)
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Sets up custom foreign key choices."""
        if db_field.name == "permissions":
            kwargs["queryset"] = self.admin_site.get_permissions(request)
        return super(GroupAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    
    
site.register(Group, GroupAdmin)

