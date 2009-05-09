"""
The upgraded CMS online admin area.

This is an enhanced version of the Django admin area, providing a more
user-friendly appearance and providing additional functionality over the
standard implementation.
"""


from django.contrib import admin
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType


class AdminSite(admin.AdminSite):
    
    """The CMS admin site."""
    
    def index(self, request, extra_context=None):
        """Displays the admin site dashboard."""
        context = {"title": "Dashboard"}
        context.update(extra_context or {})
        return super(AdminSite, self).index(request, context)
    
    def get_content_types(self):
        """Returns the content types of all models registered with this site."""
        content_types = [ContentType.objects.get_for_model(model)
                         for model in self._registry.keys()]
        return content_types
    
    def get_permissions(self):
        """
        Returns an list of permissions for all models registered with
        this site.
        """
        content_types = self.get_content_types()
        permissions = Permission.objects.filter(content_type__in=content_types)
        permissions = permissions.order_by("content_type__app_label", "content_type__model", "name")
        return permissions
    
    
# The default instance of the CMS admin site.
    
site = AdminSite()


# Re-register some standard Django models.

class UserAdmin(admin.ModelAdmin):
    
    """Admin settings for User models."""
    
    
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
            kwargs["queryset"] = self.admin_site.get_permissions()
        return super(GroupAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    
    
site.register(Group, GroupAdmin)

