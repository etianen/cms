"""Forms used by the staff management application."""


from django import forms
from django.conf import settings
from django.contrib.admin.widgets import FilteredSelectMultiple, AdminTextareaWidget, AdminTextInputWidget
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.contrib.auth.models import User, Group


class EditDetailsForm(forms.ModelForm):
    
    """Form that allows a user to edit their own details."""
    
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email",)


class UserCreationForm(BaseUserCreationForm):
    
    """Extended user creation form."""
    
    is_staff = forms.BooleanField(required=False,
                                  initial=True,
                                  help_text=User._meta.get_field("is_staff").help_text)
    
    groups = forms.ModelMultipleChoiceField(required=False,
                                            queryset=Group.objects.all(),
                                            initial=settings.DEFAULT_GROUP_IDS,
                                            widget=FilteredSelectMultiple("groups", False))
    
    def save(self, commit=True):
        """Saves the user."""
        user = super(UserCreationForm, self).save(commit=False)
        if commit:
            user.save()
            self.save_m2m()
        return user
    
    class Meta:
        model = User
        fields = ("username", "is_staff", "first_name", "last_name", "email", "groups",)
        
        
class UserContactForm(forms.Form):
    
    subject = forms.CharField(max_length=1000,
                              widget=AdminTextInputWidget)
    
    content = forms.CharField(widget=AdminTextareaWidget)