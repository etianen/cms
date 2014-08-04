"""HTML processing routines."""


import re

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.html import escape

from cms import permalinks


RE_TAG = re.compile(ur"<(img|a)(\s+.*?)(/?)>", re.IGNORECASE)

RE_ATTR = re.compile(ur"\s([\w-]+)=(\".*?\"|'.*?')", re.IGNORECASE)


def process(text):
    """
    Expands permalinks in <a/> and <img/> tags.
    
    Images will also be automatically thumbnailed to fit their specified width
    and height.
    """
    resolved_permalinks = {}
    def sub_tag(match):
        tagname = match.group(1)
        attrs = dict(RE_ATTR.findall(match.group(2)))
        def get_obj(attr_name):
            if attr_name in attrs:
                value = attrs[attr_name][1:-1]
                if not value in resolved_permalinks:
                    try:
                        resolved_permalinks[value] = permalinks.resolve(value)
                    except (permalinks.PermalinkError, ObjectDoesNotExist):
                        resolved_permalinks[value] = None
                obj = resolved_permalinks[value]
                if obj:
                    # Add in the URL of the obj.
                    attrs[attr_name] = '"%s"' % escape(obj.get_absolute_url())
                    # Add in the title of the obj.
                    attrs.setdefault("title", u'"%s"' % escape(getattr(obj, "title", unicode(obj))))
                return obj
            return None
        if tagname == "a":
            # Process hyperlinks.
            get_obj("href")
        elif tagname == "img":
            # Process images.            
            get_obj("src")
        else:
            assert False
        # Regenerate the html tag.
        attrs = u" ".join(u"%s=%s" % (key, value) for key, value in sorted(attrs.iteritems()))
        return u"<%s %s%s>" % (tagname, attrs, match.group(3))
    return RE_TAG.sub(sub_tag, text)

