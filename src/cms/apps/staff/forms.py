"""Forms used by the staff management application."""


from django import forms
from django.conf import settings
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.contrib.auth.models import User, Group
from django.utils.safestring import mark_safe


groups_field = forms.ModelMultipleChoiceField(queryset=Group.objects.all(),
                                             initial=settings.DEFAULT_GROUP_IDS,
                                             widget=FilteredSelectMultiple("groups", False))


class UserCreationForm(BaseUserCreationForm):
    
    """Extended user creation form."""
    
    groups = groups_field
    
    def save(self, commit=True):
        """Saves the user."""
        user = super(UserCreationForm, self).save(commit=False)
        user.is_staff = True
        if commit:
            user.save()
            self.save_m2m()
        return user
    
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "groups",)
        
        