"""Thumbnail generation utilities."""


import os, re

from PIL import Image  # @UnresolvedImport

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from django.core.files.images import get_image_dimensions
from django.utils.html import escape

from cms.apps.pages import permalinks
from cms.apps.pages.optimizations import cached_getter


__all__ = ("create", "PROPORTIONAL", "RESIZED", "CROPPED", "create_thumbnails_html",)


class Thumbnail(object):
    
    """
    A generated thumbnail image.
    
    This conforms to the Django image file specification.
    """
    
    __slots__ = ("name", "_dimensions_cache",)
    
    def __init__(self, name):
        """Initializes the Thumbnail."""
        self.name = name
        
    def get_url(self):
        """Returns the URL of the thumbnail."""
        return default_storage.url(self.name)
    
    url = property(get_url,
                   doc="The URL of the thumbnail")
    
    def get_path(self):
        """Returns the path of the thumbnail on disk."""
        return default_storage.path(self.name)
    
    path = property(get_path,
                    doc="The path of the thumbnail on disk.")
    
    def get_size(self):
        """Returns the size of the thumbnail on disk, in bytes."""
        return default_storage.size(self.name)
        
    size = property(get_size,
                    doc="The size of the thumbnail on disk, in bytes.")
    
    @cached_getter
    def get_dimensions(self):
        """Returns a tuple of the dimensions of the image, in pixels."""
        return get_image_dimensions(self.path)
    
    dimensions = property(get_dimensions,
                          doc="A tuple of the dimensions of the image, in pixels.")
    
    def get_width(self):
        """Returns the width of the image, in pixels."""
        return self.dimensions[0]
    
    width = property(get_width,
                     doc="The width of the image, in pixels.")
    
    def get_height(self):
        """Returns the height of the image in pixels."""
        return self.dimensions[1]
    
    height = property(get_height,
                      doc="The height of the image, in pixels.")
        

# Resize the image, preserving aspect ratio.
PROPORTIONAL = "proportional"

# Resize the image, ignoring aspect ratio.
RESIZED = "resized"

# Resize the image, cropping as necessary to preserve aspect ratio.
CROPPED = "cropped"


def create(image, width, height, method=PROPORTIONAL):
    """
    Creates a thumbnail of the given image, returning a Django image file.
    
    There are three available methods of thumbnail generation.
    
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
        
    The default filesystem storage provided by Django will be used to store the
    created thumbnail under a generated name.
    """
    try:
        image_path = image.path
    except AttributeError:
        # Image must provide a path attribute.
        return image
    # Generate the thumbnail filename.
    thumbnail_name = "thumbnails/%s-%sx%s/%s" % (method, width, height, image.name.lstrip("/"))
    thumbnail_path = default_storage.path(thumbnail_name)
    # See if the thumbnail has already been created.
    if default_storage.exists(thumbnail_name):
        image_timestamp = os.stat(image_path).st_mtime
        thumbnail_timestamp = os.stat(thumbnail_path).st_mtime
        # If the thumbnail is newer than the file, no more generation needs to take place.
        if thumbnail_timestamp > image_timestamp:
            return Thumbnail(thumbnail_name)
    else:
        dirname = os.path.dirname(thumbnail_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
    # Create an image buffer in memory.
    image_data = Image.open(image.path)
    # Generate a new thumbnail.
    try:
        if method == PROPORTIONAL:
            image_data.thumbnail((width, height), Image.ANTIALIAS)
        elif method == RESIZED:
            image_data = image_data.resize((width, height), Image.ANTIALIAS)
        elif method == CROPPED:
            original_width, original_height = image_data.size
            required_aspect = float(width) / float(height)
            source_width = min(original_width, int(original_height * required_aspect))
            source_height = min(original_height, int(original_width / required_aspect))
            source_x = (original_width - source_width) / 2
            source_y = (original_height - source_height) / 2
            image_data = image_data.transform((width, height), Image.EXTENT, (source_x, source_y, source_x + source_width, source_y + source_height), Image.BICUBIC)
        else:
            raise ValueError, "Unknown thumbnail generation method: %r" % method
    except SyntaxError, ex:
        # HACK: The PIL will raise a SyntaxError if it encounters a 'broken png'. 
        raise IOError, str(ex)
    # Save the thumbnail to disk.
    image_data.save(thumbnail_path)
    # Return the new image object.
    return Thumbnail(thumbnail_name)


RE_IMG = re.compile(ur"<img(.+?)/>", re.IGNORECASE)

RE_ATTR = re.compile(ur"""\s(\w+)=(["'].*?["'])""", re.IGNORECASE)


def sub_image(match):
    """Replaces the given image with a thumbnail."""
    attrs = match.group(1)
    attr_dict = dict(RE_ATTR.findall(attrs))
    try:
        src = attr_dict["src"][1:-1]
        obj = permalinks.resolve(src)
        width = int(attr_dict["width"][1:-1])
        height = int(attr_dict["height"][1:-1])
        thumbnail = create(obj.file, width, height, RESIZED)
    except (ObjectDoesNotExist, permalinks.PermalinkError, KeyError, ValueError, IOError):
        # If not width or height provided, or an IOError occurs, we cannot proceed.
        return match.group(0)
    attr_dict["src"] = '"%s"' % escape(thumbnail.url)
    return u"<img %s/>" % (" ".join(u'%s=%s' % (name, value) for name, value in sorted(attr_dict.iteritems())))


def create_thumbnails_html(html):
    """
    Generates thumbnails for all permalinked images in the given HTML text.
    
    If an image does not contain a permalink, or an IOError occurs during the
    thumbnail generation, then the image tag is left untouched.
    """
    return RE_IMG.sub(sub_image, html)

