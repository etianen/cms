"""Forms used by the CMS."""


from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


class EditDetailsForm(forms.ModelForm):
    
    """Form that allows a user to edit their own details."""
    
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email",)
        
        
class PageForm(forms.ModelForm):
    
    """Form used to edit Page models."""
    
    pass
    
    
class HtmlWidget(forms.Textarea):
    
    """A textarea that is converted into a TinyMCE editor."""
    
    def __init__(self, init_js=None, attrs=None, **kwargs):
        """Initializes the HtmlWidget."""
        widget_attrs = {"class": "html"}
        widget_attrs.update(attrs or {})
        super(HtmlWidget, self).__init__(attrs=widget_attrs, **kwargs)
        self.init_js = init_js

    def get_media(self):
        """Returns the media used by the widget."""
        tiny_mce_js = settings.CMS_MEDIA_URL + "js/tiny_mce/tiny_mce.js"
        init_js =  self.init_js or reverse("tinymce_init")
        return forms.Media(js=(tiny_mce_js, init_js))
        
    media = property(get_media,
                     doc="The media used by the widget.")
    
    