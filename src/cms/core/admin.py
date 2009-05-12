"""
The upgraded CMS online admin area.

This is an enhanced version of the Django admin area, providing a more
user-friendly appearance and providing additional functionality over the
standard implementation.
"""


from django import template
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import redirect, render_to_response

from cms.core.forms import UserCreationForm


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
            raise Http404, str(ex)
        try:
            obj = content_type.get_object_for_this_type(pk=object_id)
        except content_type.model_class().DoesNotExist, ex:
            raise Http404, str(ex)
        try:
            redirect_url = obj.get_absolute_url()
        except AttributeError:
            raise Http404, "%s objects do not publish an absolute URL." % content_type.name.title()
        return redirect(redirect_url)
    
    
# The default instance of the CMS admin site.
    
site = AdminSite()


# Re-register some standard Django models.

class UserAdmin(BaseUserAdmin):
    
    """
    Admin settings for User models.
    
    As a simplification, all users are taken to be staff users.
    """
    
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

