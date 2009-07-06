"""Some default contact forms."""


from django import forms


class ContactForm(forms.Form):
    
    """A basic contact form."""
    
    verbose_name = "simple contact form"
    
    name = forms.CharField()
    
    email = forms.EmailField()
    
    message = forms.CharField(widget=forms.Textarea)
    
