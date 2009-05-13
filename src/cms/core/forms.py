"""Forms used by the CMS."""


from django import forms
from django.contrib.auth.models import User


class EditDetailsForm(forms.ModelForm):
    
    """Form that allows a user to edit their own details."""
    
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email",)
        
        