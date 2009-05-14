"""
The upgraded CMS online admin area.

This is an enhanced version of the Django admin area, providing a more
user-friendly appearance and providing additional functionality over the
standard implementation.
"""


from django import template
from django.core.urlresolvers import reverse
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import redirect, render_to_response

from cms.core.forms import EditDetailsForm
from cms.staff.models import Permission


class AdminSite(admin.AdminSite):
    
    """The CMS admin site."""
    
    # HACK: The base admin site manually sets the root path to a wrong value,
    # thus this hack has to remain until the base admin site fixes this.
    def __init__(self, *args, **kwargs):
        """Initializes the admin site."""
        super(AdminSite, self).__init__(*args, **kwargs)
        self.root_path = "/admin/"
    
    def index(self, request, extra_context=None):
        """Displays the admin site dashboard."""
        context = {"title": "Dashboard"}
        context.update(extra_context or {})
        return super(AdminSite, self).index(request, context)
    
    # FIXME: Proxy models return the content type of their parent model when
    # get_for_model is used.
    def get_content_types(self):
        """Returns the content types of all models registered with this site."""
        content_types = [ContentType.objects.get_for_model(model)
                         for model in self._registry.keys()]
        return content_types
    
    # FIXME: No permissions are created for proxy models.
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
    
    # Custom admin views.
    
    def get_urls(self):
        """Adds some custom functionality to this admin site."""
        urlpatterns = patterns("",
                               url(r"^r/(\d+)/(.+)/$", self.view_on_site),
                               url(r"^edit-details/$", self.admin_view(self.edit_details), name="admin_edit_details"),)
        urlpatterns += super(AdminSite, self).get_urls()
        return urlpatterns
    
    def edit_details(self, request):
        """Allows a user to edit their own details."""
        user = request.user
        if request.method == "POST":
            form = EditDetailsForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                message = "Your details have been updated."
                request.user.message_set.create(message=message)
                if "_continue" in request.POST:
                    return redirect("admin_edit_details")
                else:
                    return redirect("admin_index")
        else:
            form = EditDetailsForm(instance=user)
        media = form.media
        context = {"title": "Edit details",
                   "form": form,
                   "is_popup": False,
                   "add": False,
                   "change": True,
                   "has_add_permission": False,
                   "has_delete_permission": False,
                   "has_change_permission": True,
                   "has_file_field": False,
                   "has_absolute_url": False,
                   "auto_populated_fields": (),
                   "opts": User._meta,
                   "media": media,
                   "save_as": False,
                   "root_path": self.root_path,
                   "app_label": User._meta.app_label,}
        return render_to_response("admin/edit_details_form.html", context, template.RequestContext(request))
    
    # HACK: The current admin redirect implementation requires the sites
    # framework.  This can be removed if the sites dependency is removed.  This
    # might break in Django 1.3, which will start using named URL patterns in
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

