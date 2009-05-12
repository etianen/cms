"""
The upgraded CMS online admin area.

This is an enhanced version of the Django admin area, providing a more
user-friendly appearance and providing additional functionality over the
standard implementation.
"""


from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import redirect


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
    
    def get_permissions(self, request):
        """
        Returns an list of permissions for all models registered with
        this site.
        """
        user = request.user
        content_types = self.get_content_types()
        permissions = Permission.objects.filter(content_type__in=content_types)
        permissions = permissions.order_by("content_type__app_label", "content_type__model", "name")
        return permissions
    
    def get_urls(self):
        """Adds some custom functionality to this admin site."""
        urlpatterns = patterns("", url(r"^r/(\d+)/(.+)/$", self.view_on_site))
        urlpatterns += super(AdminSite, self).get_urls()
        return urlpatterns
    
    # HACK: The current admin redirect implementation requires the sites
    # framework.  This can be removed if the sites dependency is removed.  This
    # might break in Django 1.2, which will start using named URL patterns in
    # the admin views.
    def view_on_site(self, request, content_type_id, object_id):
        """Redirects to the absolute URL of the object in the public site."""
        try:
            content_type = ContentType.objects.get_for_id(content_type_id)
        except ContentType.DoesNotExist, ex:
            raise Http404, ex
        try:
            obj = content_type.get_object_for_this_type(pk=object_id)
        except content_type.model_class().DoesNotExist, ex:
            raise Http404, ex
        try:
            redirect_url = obj.get_absolute_url()
        except AttributeError:
            raise Http404, "%s objects do not publish an absolute URL." % content_type.name.title()
        return redirect(redirect_url)
    
    
# The default instance of the CMS admin site.
    
site = AdminSite()


# Re-register some standard Django models.

class UserAdmin(DjangoUserAdmin):
    
    """Admin settings for User models."""
    
    fieldsets = ((None, {"fields": ("username", "is_staff", "is_active",)}),
                 ("Personal information", {"fields": ("first_name", "last_name", "email",)}),
                 ("Groups", {"fields": ("groups",)}),
                 ("Advanced permissions", {"fields": ("is_superuser", "user_permissions",),
                                  "classes": ("collapse",)}),)
    
    filter_horizontal = ("user_permissions", "groups",)
    
    list_display = ("username", "first_name", "last_name", "email", "is_staff", "is_active",)
    
    list_filter = ("is_staff", "is_active",)
    
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Sets up custom foreign key choices."""
        if db_field.name == "user_permissions":
            kwargs["queryset"] = self.admin_site.get_permissions(request)
        return super(UserAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)
    
    
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

