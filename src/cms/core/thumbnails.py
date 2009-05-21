"""Thumbnail generation utilities."""


import os

from PIL import Image

from django.core.files.storage import default_storage
from django.core.files.images import ImageFile


# Resize the image, preserving aspect ratio.
THUMBNAIL = "preserved"

# Resize the image, ignoring aspect ratio.
RESIZE = "resized"

# Resize the image, cropping as necessary to preserve aspect ratio.
CROP = "cropped"


def generate(image, requested_width, requested_height, generation_method=RESIZE):
    """
    Generated a thumbnail of the given image, returning an image representing
    the thumbnail.
    """
    # Cannot generate thumbnails for images without a path.
    if not hasattr(image, "path"):
        return image
    image_path = image.path
    # Calculate image dimensions.
    try:
        original_width = image.width
        original_height = image.height
    except IOError:
        # The image could not be found on disk, let the calling method deal with it.
        return image
    requested_width = min(requested_width, original_width)
    requested_height = min(requested_height, original_height)
    # Don't generate thumbnail if no resizing is to take place.
    if original_width == requested_width and original_height == requested_height:
        return image
    # Generate the thumbnail filename.
    thumbnail_name = "thumbnails/%s/%sx%s/%s" % (generation_method, requested_width, requested_height, image.name)
    thumbnail_path = default_storage.path(thumbnail_name)
    thumbnail_url = default_storage.url(thumbnail_name)
    # See if the thumbnail has already been created.
    if default_storage.exists(thumbnail_name):
        image_timestamp = os.stat(image_path).st_mtime
        thumbnail_timestamp = os.stat(thumbnail_path).st_mtime
        # If the thumbnail is newer than the file, no more generation needs to take place.
        if thumbnail_timestamp > image_timestamp:
            thumbnail = default_storage.open(thumbnail_name, mixin=ImageFile)
            thumbnail.url = thumbnail_url
            return thumbnail
    else:
        dirname = os.path.dirname(thumbnail_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
    # Calculate aspect ratios.
    original_aspect = float(original_width) / float(original_height)
    required_aspect = float(requested_width) / float(requested_height)
    # Create an image buffer in memory.
    try:
        image_data = Image.open(image.path)
    except IOError:
        # Image does not exist, spit it back.
        return image
    # Generate a new thumbnail.
    if generation_method == THUMBNAIL:
        image_data.thumbnail((requested_width, requested_height), Image.ANTIALIAS)
    elif generation_method == RESIZE:
        image_data = image_data.resize((requested_width, requested_height), Image.ANTIALIAS)
    elif generation_method == CROP:
        source_width = min(original_width, int(original_height * required_aspect))
        source_height = min(original_height, int(original_width / required_aspect))
        source_x = (original_width - source_width) / 2
        source_y = (original_height - source_height) / 2
        print source_width, source_height
        image_data = image_data.transform((requested_width, requested_height), Image.EXTENT, (source_x, source_y, source_x + source_width, source_y + source_height), Image.BICUBIC)
    else:
        raise ValueError, "Unknown thumbnail generation method: %r" % generation_method
    # Save the thumbnail to disk.
    image_data.save(thumbnail_path)
    # Return the new image object.
    thumbnail = default_storage.open(thumbnail_path, mixin=ImageFile)
    thumbnail.url = thumbnail_url
    return thumbnail
    
    
def thumbnail(image, requested_width, requested_height):
    """Generates a resized thumbnail, preserving aspect ratio."""
    return generate(image, requested_width, requested_height, THUMBNAIL)
    
    
def resize(image, requested_width, requested_height):
    """Generates a rescaled thumbnail, ignoring aspect ratio."""
    return generate(image, requested_width, requested_height, RESIZE)


def crop(image, requested_width, requested_height):
    """Generates a cropped thumbnail, preserving aspect ratio."""
    return generate(image, requested_width, requested_height, CROP)

