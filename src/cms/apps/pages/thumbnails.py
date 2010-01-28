"""Thumbnail generation utilities."""


from __future__ import with_statement

import os

from PIL import Image  # @UnresolvedImport

from django.core.files.storage import default_storage


__all__ = ("create", "PROPORTIONAL", "RESIZED", "CROPPED",)


class Thumbnail(object):
    
    """
    A generated thumbnail image.
    
    This conforms to the Django image file specification.
    """
    
    __slots__ = ("name", "url", "path", "width", "height",)
    
    def __init__(self, name, url, path, width, height):
        """Initializes the Thumbnail."""
        self.name = name
        self.url = url
        self.path = path
        self.width = width
        self.height = height
        

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
    # Get the path to the image.
    try:
        image_path = image.path
        image_url = image.url
    except AttributeError:
        # Image must provide a path and url attribute.
        return image
    # Open up the image file.
    with open(image_path, "rb") as src_file:
        image_data = Image.open(src_file)
        # Calculate required image size.
        original_width, original_height = image_data.size
        width = min(width, original_width)
        height = min(height, original_height)
        original_aspect = float(original_width) / float(original_height)
        required_aspect = float(width) / float(height)
        # Adjust for aspect ratio if using proportional resize.
        if method == PROPORTIONAL:
            if original_aspect > required_aspect:  # Too wide.
                height = int(round(width / original_aspect))
            elif original_aspect < required_aspect:  # Too narrow.
                width = int(round(height * original_aspect))
        # If no resizing has to take place, return the original image.
        if width == original_width and height == original_height:
            return Thumbnail(image.name, image_url, image_path, width, height)
        # Generate the thumbnail filename.
        thumbnail_name = "thumbnails/%s-%sx%s/%s" % (method, width, height, image.name.lstrip("/"))
        thumbnail_path = default_storage.path(thumbnail_name)
        thumbnail_url = default_storage.url(thumbnail_name)
        # See if the thumbnail has already been created.
        if default_storage.exists(thumbnail_name):
            image_timestamp = os.stat(image_path).st_mtime
            thumbnail_timestamp = os.stat(thumbnail_path).st_mtime
            # If the thumbnail is newer than the file, no more generation needs to take place.
            if thumbnail_timestamp >= image_timestamp:
                return Thumbnail(thumbnail_name, thumbnail_url, thumbnail_path, width, height)
        else:
            dirname = os.path.dirname(thumbnail_path)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
        # Generate a new thumbnail.
        try:
            if method == RESIZED or method == PROPORTIONAL:
                image_data = image_data.resize((width, height), Image.ANTIALIAS)
            elif method == CROPPED:
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
        # Return the newly created thumbnail.
        return Thumbnail(thumbnail_name, thumbnail_url, thumbnail_path, width, height)

