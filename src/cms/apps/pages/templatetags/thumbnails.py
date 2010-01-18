"""Template tags used to generate thumbnails."""


import re

from django import template
from django.core.exceptions import ObjectDoesNotExist
from django.forms.util import flatatt
from django.core.files.images import get_image_dimensions
from django.utils.html import escape

from cms.apps.pages.templatetags import PatternNode
from cms.apps.pages import permalinks, thumbnails


register = template.Library()


@register.tag
def thumbnail(parser, token):
    """
    Generates a HTML image tag containing a thumbnail of the given Django image
    file::
    
        {% thumbnail image_file 150 100 %}
        
    By default, this will use a proportional resize to generate the thumbnail.
    Alternative thumbnailing methods are also available.
    
    :proportional:
        The default method of thumbnail generation. This preserves aspect ratio
        but may result in an image that is a slightly different size to the
        dimensions requested.
        
    :resized:
        The thumbnail will be exactly the size requested, but the aspect ratio
        may change. This can result in images that look squashed or stretched.
        
    :cropped:
        The thumbnail will be exactly the size requested, cropped to preseve
        aspect ratio.
        
    You specify the thumbnailing method as follows::
    
        {% thumbnail image_file 150 100 resized %}
    
    You can also insert the generated thumbnail into the context as a variable
    by specifying an alias::
    
        {% thumbnail image_file 150 100 as image_thumbnail %}
        
    """
    def handler(context, image, width, height, method="thumbnail", alias=None):
        thumbnail = thumbnails.create(image, width, height, method)
        if alias:
            context[alias] = thumbnail
            return ""
        return '<img src="%s" width="%s" height="%s" alt=""/>' % (escape(thumbnail.url), thumbnail.width, thumbnail.height)
    return PatternNode(parser, token, handler, ("{image} {width} {height} [method] as [alias]",
                                                "{image} {width} {height} [method]",
                                                "{image} {width} {height} as [alias]",
                                                "{image} {width} {height}",))
    

RE_IMG = re.compile(ur"<img(.+?)/>", re.IGNORECASE)

RE_ATTR = re.compile(ur"""\s(\w+)=["']([^"']+)["']""", re.IGNORECASE)


def replace_thumbnail(match):
    """Replaces the given image with a thumbnail."""
    attrs = match.group(1)
    attr_dict = dict(RE_ATTR.findall(attrs))
    try:
        src = attr_dict["src"]
    except KeyError:
        pass
    else:
        try:
            obj = permalinks.resolve(src)
        except ObjectDoesNotExist:
            pass
        except permalinks.PermalinkError:
            pass
        else:
            file = obj.file
            attr_dict["src"] = obj.file.url
            try:
                width = int(attr_dict["width"])
                height = int(attr_dict["height"])
            except KeyError:
                attr_dict["width"], attr_dict["height"] = get_image_dimensions(file)
            except ValueError:
                pass
            else:
                try:
                    thumbnail = thumbnails.resize(file, width, height)
                except IOError:
                    pass
                else:
                    attr_dict["src"] = thumbnail.url
                    attr_dict["width"] = thumbnail.width
                    attr_dict["height"] = thumbnail.height
    return u"<img%s/>" % flatatt(attr_dict)


@register.filter
def generate_thumbnails(text):
    """
    Generates thumbnails for all the permalinked images in the given HTML text.
    """
    return RE_IMG.sub(replace_thumbnail, text)
    
    