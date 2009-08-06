"""Template tags used to generate thumbnails."""


import re

from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.forms.util import flatatt

from cms.apps.pages import permalinks
from cms.apps.pages import permalinks, thumbnails
from cms.apps.pages.templatetags import Library


register = Library()


@register.simple_tag
def img(image):
    """Renders the given Django image file as a HTML image."""
    return '<img src="%s" width="%s" height="%s" alt=""/>' % (image.url, image.width, image.height)


THUMBNAIL_TAG_PATTERNS = ("{image} {width} {height} as {alias}",
                          "{image} {width} {height}",) 


@register.pattern_tag(*THUMBNAIL_TAG_PATTERNS)
def thumbnail(context, image, width, height, alias=None):
    """
    Generates a thumbnail of the given image, preserving aspect ratio.
    
    This has the syntax:
    
        {% thumbnail image width height %}
        
    The output will be a HTML image tag.
    
    Alternatively, you can specify an alias for the image as follows:
    
        {% thumbnail image width height as alias %}
        
    This will put an thumbnail variable into the context under the given name.
    The thumbnail variable will be of type ImageFile, allowing its url, width
    and height to be accessed.
    """
    thumbnail = thumbnails.thumbnail(image, width, height)
    if alias:
        context[alias] = thumbnail
        return ""
    return img(thumbnail)
    
    
@register.pattern_tag(*THUMBNAIL_TAG_PATTERNS)
def resize(context, image, width, height, alias=None):
    """
    Generates a resized thumbnail of the given image, ignoring aspect ratio.
    
    See the 'thumbnail' tag for appropriate syntax.
    """
    thumbnail = thumbnails.resize(image, width, height)
    if alias:
        context[alias] = thumbnail
        return ""
    return img(thumbnail)


@register.pattern_tag(*THUMBNAIL_TAG_PATTERNS)
def crop(context, image, width, height, alias=None):
    """
    Generates a cropped thumbnail of the given image, preserving aspect ratio.
    
    See the 'thumbnail' tag for appropriate syntax.
    """
    thumbnail = thumbnails.crop(image, width, height)
    if alias:
        context[alias] = thumbnail
        return ""
    return img(thumbnail)


RE_IMG = re.compile(r"<img(.+?)/>", re.IGNORECASE)

RE_ATTR = re.compile(r"""\s(\w+)=["']([^"']+)["']""", re.IGNORECASE)


@register.filter
def generate_thumbnails(text):
    """
    Generates thumbnails for all the permalinked images in the given HTML text.
    """
    offset = 0
    for match in RE_IMG.finditer(text):
        attrs = match.group(1)
        attr_dict = dict(RE_ATTR.findall(attrs))
        try:
            src = attr_dict["src"]
            width = int(attr_dict["width"])
            height = int(attr_dict["height"])
        except KeyError:
            continue
        except ValueError:
            continue
        try:
            obj = permalinks.resolve(src)
        except ObjectDoesNotExist:
            continue
        except permalinks.PermalinkError:
            continue
        thumbnail = thumbnails.resize(obj.file, width, height)
        attr_dict["src"] = thumbnail.url
        attr_dict["width"] = thumbnail.width
        attr_dict["height"] = thumbnail.height
        new_attrs = flatatt(attr_dict)
        start = match.start(1)
        end = match.end(1)
        text = u"".join((text[:start+offset], new_attrs, text[end+offset:]))
        offset += len(new_attrs) - len(attrs)
    return text 
        
    