"""Form widgets used by the CMS."""

import json

from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe


class HtmlWidget(forms.Textarea):
    
    """A textarea that is converted into a TinyMCE editor."""
    
    def __init__(self, *args, **kwargs):
        """Initializes the HtmlWidget."""
        self.richtext_settings = getattr(settings, "RICHTEXT_SETTINGS", {}).get(kwargs.pop("richtext_settings", "default"), {})
        super(HtmlWidget, self).__init__(*args, **kwargs)
    
    def render(self, name, value, attrs=None):
        """Renders the widget."""
        # Get the standard widget.
        html = super(HtmlWidget, self).render(name, value, attrs)
        # Add on the JS initializer.
        attrs = attrs or {}
        try:
            element_id = attrs["id"]
        except KeyError:
            pass
        else:
            # Add in the initializer.
            settings_js = json.dumps(self.richtext_settings)
            html += u'<script>django.jQuery("#{element_id}").cms("htmlWidget",{settings_js})</script>'.format(
                element_id = element_id,
                settings_js = settings_js,
            )
        # All done!
        return mark_safe(html)

    class Media:
        js = (
            "cms/js/tiny_mce/tiny_mce.js",
            "cms/js/jquery.cms.js",
            "pages/js/jquery.cms.pages.js",
            "media/js/jquery.cms.media.js",
        )
