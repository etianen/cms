"""Forms used by the staff management application."""


from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.utils.safestring import mark_safe

from cms.staff.models import User, Group, EDITORS_GROUP_ID


groups_field = forms.ModelMultipleChoiceField(queryset=Group.objects.all(),
                                             initial=[EDITORS_GROUP_ID],
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
        
        