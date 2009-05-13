"""Models used by the staff managment application."""


from django.contrib.auth.models import User as BaseUser
from django.contrib.auth.models import Group as BaseGroup
from django.contrib.auth.models import Permission as BasePermission


class User(BaseUser):
    
    """A user who has access to the online admin area."""
    
    class Meta:
        proxy = True
        
        
class Group(BaseGroup):
    
    """A group of users, with associated permissions."""
    
    class Meta:
        proxy = True
        
        
class Permission(BasePermission):
    
    """A permission granted to a `User` or `Group`."""
    
    class Meta:
        proxy = True
        
        