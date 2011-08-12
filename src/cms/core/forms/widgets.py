"""Form widgets used by the CMS."""

from django import forms
from django.forms import NullBooleanSelect
from django.conf import settings
from django.core.urlresolvers import reverse


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
        filebrowser_js = settings.STATIC_URL + "cms/js/jquery.filebrowser.js"
        tiny_mce_js = settings.STATIC_URL + "cms/js/tiny_mce/tiny_mce.js"
        init_js =  self.init_js or reverse("admin:tinymce_init")
        return forms.Media(js=(tiny_mce_js, filebrowser_js, init_js))
        
    media = property(get_media,
                     doc="The media used by the widget.")
    
    
class NullBooleanWidget(NullBooleanSelect):
    
    """A null boolean widget with a blank choice instead of 'maybe'."""
    
    def __init__(self, attrs=None):
        """Sets some different default choices."""
        super(NullBooleanWidget, self).__init__(attrs,)
        self.choices = ((u"1", "---------"), (u"2", "Yes"), (u"3", "No"))