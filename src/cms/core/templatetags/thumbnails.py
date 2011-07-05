"""Template tags used to generate thumbnails."""


from django import template
from django.utils.html import escape

from cms.core import thumbnails, debug
from cms.core.templatetags import PatternNode


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
    def handler(context, image, width, height, method=thumbnails.PROPORTIONAL, alias=None):
        try:
            thumbnail_obj = thumbnails.create(image, width, height, method)
        except IOError:
            debug.print_current_exc()
            thumbnail_obj = thumbnails.Thumbnail(
                image.name,
                image.path,
                image.url,
                thumbnails.Size(width, height)
            )
        if alias:
            context[alias] = thumbnail_obj
            return ""
        return u'<img src="{src}" width="{width}" height="{height}" alt=""/>'.format(
            src = escape(thumbnail_obj.url),
            width = thumbnail_obj.width,
            height = thumbnail_obj.height,
        )
    return PatternNode(parser, token, handler, ("{image} {width} {height} [method] as [alias]",
                                                "{image} {width} {height} as [alias]",
                                                "{image} {width} {height} [method]",
                                                "{image} {width} {height}",))
    
    