"""Models used by the staff managment application."""


from django.contrib.auth.models import UserManager as BaseUserManager
from django.contrib.auth.models import User as BaseUser
from django.contrib.auth.models import Group as BaseGroup
from django.contrib.auth.models import Permission as BasePermission
from django.contrib.contenttypes.models import ContentType 
from django.db import models


class UserManager(BaseUserManager):
    
    """Manager for User objects."""
    
    def get_query_set(self):
        """Returns all staff members that are not superusers."""
        queryset = super(UserManager, self).get_query_set()
        queryset = queryset.filter(is_staff=True, is_superuser=False)
        return queryset
    

class User(BaseUser):
    
    """A user who has access to the online admin area."""
    
    objects = UserManager()
    
    def __unicode__(self):
        """
        Tries to return the full name of the user, falling back to their
        username.
        """
        if self.first_name and self.last_name:
            return u" ".join((self.first_name, self.last_name))
        if self.first_name:
            return self.first_name
        return self.username
    
    class Meta:
        proxy = True
        
        
ADMINISTRATORS_GROUP_ID = 1

EDITORS_GROUP_ID = 2
        
        
class GroupManager(models.Manager):
    
    """Manager for Group objects."""
    
    def create_administrators(self):
        """Creates the administrators group."""
        administrators = self.create(id=ADMINISTRATORS_GROUP_ID, name="Administrators")
        user_content_type = ContentType.objects.get_for_model(User)
        user_permissions = Permission.objects.filter(content_type=user_content_type)
        for user_permission in user_permissions:
            administrators.permissions.add(user_permission)
        return administrators
    
    def get_administrators(self):
        """Returns the administrators group."""
        return self.get(id=ADMINISTRATORS_GROUP_ID)
    
    def create_editors(self):
        """Creates the editors group."""
        return self.create(id=EDITORS_GROUP_ID, name="Editors")
    
    def get_editors(self):
        """Returns the editors group."""
        return self.get(id=EDITORS_GROUP_ID)
    
        
class Group(BaseGroup):
    
    """A group of users, with associated permissions."""
    
    objects = GroupManager()
    
    class Meta:
        proxy = True
        
        
class Permission(BasePermission):
    
    """A permission granted to a `User` or `Group`."""
    
    def __unicode__(self):
        """Returns a hypen-separated description of the Permission."""
        content_type = ContentType.objects.get_for_id(self.content_type_id)
        app_label_name = content_type.app_label.capitalize()
        content_type_name = content_type.name.capitalize()
        name = self.name.capitalize()
        return u" - ".join((app_label_name, content_type_name, name))
    
    class Meta:
        proxy = True
        
        