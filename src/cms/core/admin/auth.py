"""Admin settings for the staff management application."""

from django.core import urlresolvers, mail
from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db import transaction
from django.shortcuts import render, redirect

from cms.core.forms.auth import UserCreationForm, EditDetailsForm, UserContactForm


class UserAdmin(BaseUserAdmin):
    
    """Admin settings for User models."""
    
    actions = ("activate_selected", "deactivate_selected", "email_selected",)
    
    add_form = UserCreationForm
    
    fieldsets = ((None, {"fields": ("username", "is_staff", "is_active",)}),
                 ("Personal information", {"fields": ("first_name", "last_name", "email",)}),
                 ("Groups", {"fields": ("groups",)}),
                 ("Advanced permissions", {"fields": ("user_permissions", "is_superuser"),
                                           "classes": ("collapse",)}),)
    
    filter_horizontal = ("user_permissions", "groups",)
    
    list_display = ("username", "first_name", "last_name", "email", "is_staff", "is_active",)
    
    list_filter = ("is_staff", "is_active",)
    
    # Custom admin actions.
    
    def activate_selected(self, request, queryset):
        """Activates the selected user accounts."""
        queryset.update(is_active=True)
    activate_selected.short_description = "Activate selected users"
    
    def deactivate_selected(self, request, queryset):
        """Deactivates the selected user accounts."""
        queryset.update(is_active=False)
    deactivate_selected.short_description = "Deactivate selected users"
    
    def email_selected(self, request, queryset):
        """Sends an email to the selected user accounts."""
        return redirect(urlresolvers.reverse("admin:staff_email_users") + "?users=%s" % ",".join(unicode(v) for v in queryset.values_list("pk", flat=True).iterator()))
    email_selected.short_description = "Email selected users"
    
    # Custom admin views.
    
    def get_urls(self):
        """Generates custom admin URLS."""
        urls = super(UserAdmin, self).get_urls()
        custom_urls = patterns("",
                               url(r"^edit-details/$", self.admin_site.admin_view(self.edit_details), name="staff_edit_details"),
                               url(r"^email/$", self.admin_site.admin_view(self.email_users), name="staff_email_users"),)
        return custom_urls + urls
    
    def email_users(self, request):
        """Sends an email to the given list of users."""
        users = self.model._default_manager.in_bulk(request.GET["users"].split(",")).values()
        if request.method == "POST":
            form = UserContactForm(request.POST)
            if form.is_valid():
                def make_addr(user):
                    if user.first_name and user.last_name:
                        return "%s %s <%s>" % (user.first_name, user.last_name, user.email)
                    return user.email
                content = form.cleaned_data["content"]
                subject = "".join((settings.EMAIL_SUBJECT_PREFIX, form.cleaned_data["subject"]))
                from_email = make_addr(request.user)
                mail.send_mass_mail((subject, content, from_email, (make_addr(request.user),))
                                    for user in users
                                    if user.email)
                self.message_user(request, "Your email was successfully sent.")
                return redirect("admin:auth_user_changelist")
        else:
            form = UserContactForm()
        context = {"title": "Email users",
                   "app_label": "auth",
                   "users": users,
                   "contact_form": form,
                   "has_change_permission": self.has_change_permission(request),
                   "opts": self.model._meta}
        return render(request, "admin/auth/user/email.html", context)
    
    @transaction.commit_on_success
    def add_view(self, request, form_url='', extra_context=None):
        """Allows new users to be added to the admin interface."""
        if request.method == "POST":
            form = self.add_form(request.POST)
            if form.is_valid():
                new_user = form.save()
                message = 'The user "%s" was added successfully.' % new_user
                self.log_addition(request, new_user)
                if "_addanother" in request.POST:
                    self.message_user(request, message)
                    return redirect("admin:auth_user_add")
                elif "_popup" in request.REQUEST:
                    return self.response_add(request, new_user)
                elif "_continue" in request.POST:
                    message = message + " You may edit it again below."
                    self.message_user(request, message)
                    return redirect("admin:auth_user_change", new_user.id)
                else:
                    self.message_user(request, message)
                    return redirect("admin:auth_user_changelist")
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
                   "app_label": self.model._meta.app_label,}
        context.update(extra_context or {})
        return render(request, "admin/auth/user/add_form.html", context)
    
    @transaction.commit_on_success
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
                    return redirect("admin:staff_edit_details")
                else:
                    return redirect("admin:index")
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
                   "opts": self.model._meta,
                   "media": media,
                   "save_as": False,
                   "app_label": self.model._meta.app_label,}
        return render(request, "admin/auth/edit_details_form.html", context)


class GroupAdmin(admin.ModelAdmin):
    
    """Admin settings for Group models."""
    
    filter_horizontal = ('permissions',)
    
    list_display = ("name",)
    
    search_fields = ("name",)
    
    ordering = ("name",)