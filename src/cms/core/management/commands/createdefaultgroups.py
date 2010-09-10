"""Creates the default admin groups."""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, User, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    
    help = """Creates the default admin groups."""

    def handle(self, *args, **options):
        group_type = ContentType.objects.get_for_model(Group)
        user_type = ContentType.objects.get_for_model(User)
        # Create the groups.
        administrators = Group.objects.create(name="Administrators")
        editors = Group.objects.create(name="Editors")
        # Get the relevant permissions.
        admin_permissions = Permission.objects.exclude(content_type=group_type)
        editor_permissions = admin_permissions.exclude(content_type=user_type)
        # Assign permissions.
        for permission in admin_permissions.iterator():
            administrators.permissions.add(permission)
        for permission in editor_permissions.iterator():
            editors.permissions.add(permission)