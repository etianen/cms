"""Some default contact forms."""


from django import forms


class ContactForm(forms.Form):
    
    """A basic contact form."""
    
    verbose_name = "simple contact form"
    
    name = forms.CharField(required=True)
    
    email = forms.EmailField(required=True)
    
    message = forms.CharField(required=True,
                              widget=forms.Textarea)
    
