"""Core widgets used by the CMS."""


from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse


class HtmlWidget(forms.Textarea):
    
    """A textarea that is converted into a TinyMCE editor."""
    
    def __init__(self, attrs, **kwargs):
        """Initializes the HtmlWidget."""
        attrs.setdefault("class", "html")
        super(HtmlWidget, self).__init__(attrs, **kwargs)

    def get_media(self):
        """Returns the media used by the widget."""
        tiny_mce_js = settings.CMS_MEDIA_URL + "js/tiny_mce/tiny_mce.js"
        tiny_mce_init_js = reverse("admin_tinymce_init")
        return forms.Media(js=(tiny_mce_js, tiny_mce_init_js))
        
    media = property(get_media,
                     doc="The media used by the widget.")
    
    