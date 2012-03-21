"""Form widgets used by the CMS."""

from django import forms
from django.conf import settings
from django.utils import simplejson as json
from django.contrib.staticfiles.storage import staticfiles_storage
from django.utils.safestring import mark_safe

from optimizations import default_stylesheet_cache, default_javascript_cache

from cms import debug


class HtmlWidget(forms.Textarea):
    
    """A textarea that is converted into a TinyMCE editor."""
    
    def __init__(self, *args, **kwargs):
        """Initializes the HtmlWidget."""
        self.richtext_settings = getattr(settings, "RICHTEXT_SETTINGS", {}).get(kwargs.pop("richtext_settings", "default"), {})
        super(HtmlWidget, self).__init__(*args, **kwargs)

    @debug.print_exc
    def get_media(self):
        """Returns the media used by the widget."""
        assets = [staticfiles_storage.url("cms/js/tiny_mce/tiny_mce.js")]
        assets.extend(default_javascript_cache.get_urls(("cms/js/jquery.cms.js", "pages/js/jquery.cms.pages.js", "media/js/jquery.cms.media.js",)))
        return forms.Media(js=assets)
    
    media = property(
        get_media,
        doc = "The media used by the widget.",
    )
    
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
            # Customize the config.
            richtext_settings = self.richtext_settings.copy()
            # Cache the asset URL.
            if "content_css" in richtext_settings:
                richtext_settings["content_css"] = default_stylesheet_cache.get_urls((richtext_settings["content_css"],))[0]
            # Add in the initializer.
            settings_js = json.dumps(richtext_settings)
            html += u'<script>django.jQuery("#{element_id}").cms("htmlWidget",{settings_js})</script>'.format(
                element_id = element_id,
                settings_js = settings_js,
            )
        # All done!
        return mark_safe(html)