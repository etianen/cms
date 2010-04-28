"""Core CMS admin functionality."""


from django.contrib.auth.models import User, Group

from cms.core.admin.sites import AdminSite
from cms.core.admin.base import PageBaseAdmin, PublishedModelAdmin, get_date_modified  # @UnusedImport
from cms.core.admin.auth import UserAdmin, GroupAdmin


site= AdminSite()


# Register the auth models.

site.register(User, UserAdmin)

site.register(Group, GroupAdmin)