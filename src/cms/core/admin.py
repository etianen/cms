"""
The upgraded CMS online admin area.

This is an enhanced version of the Django admin area, providing a more
user-friendly appearance and providing additional functionality over the
standard implementation.
"""


from django.contrib import admin
from django.contrib.auth.models import User, Group


class AdminSite(admin.AdminSite):
    
    """The CMS admin site."""
    
    
# The default instance of the CMS admin site.
    
site = AdminSite()


# Re-register some standard Django models.

class UserAdmin(admin.ModelAdmin):
    
    """Admin settings for User models."""
    
    
site.register(User, UserAdmin)


class GroupAdmin(admin.ModelAdmin):
    
    """Admin settings for Group models."""
    
    
site.register(Group, GroupAdmin)

