"""Thumbnail generation utilities."""


import os

from PIL import Image

from django.core.files.storage import default_storage
from django.core.files.images import get_image_dimensions

from cms.apps.pages.optimizations import cached_getter


class Thumbnail(object):
    
    """A generated thumbnail image."""
    
    def __init__(self, name, storage):
        """Initializes the Thumbnail."""
        self.name = name
        self.storage = storage
        
    def get_url(self):
        """Returns the URL of the thumbnail."""
        return self.storage.url(self.name)
    
    url = property(get_url,
                   doc="The URL of the thumbnail")
    
    def get_path(self):
        """Returns the path of the thumbnail on disk."""
        return self.storage.path(self.name)
    
    path = property(get_path,
                    doc="The path of the thumbnail on disk.")
    
    def get_size(self):
        """Returns the size of the thumbnail on disk, in bytes."""
        return self.storage.size(self.name)
        
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
THUMBNAIL = "proportional"

# Resize the image, ignoring aspect ratio.
RESIZE = "resized"

# Resize the image, cropping as necessary to preserve aspect ratio.
CROP = "cropped"


def generate(image, requested_width, requested_height, generation_method=RESIZE, storage=default_storage):
    """
    Generated a thumbnail of the given image, returning an image representing
    the thumbnail.
    """
    # Cannot generate thumbnails for images without a path.
    if not hasattr(image, "path"):
        return image
    image_path = image.path
    # Calculate image dimensions.
    original_width, original_height = get_image_dimensions(image_path)
    requested_width = min(requested_width, original_width)
    requested_height = min(requested_height, original_height)
    # Don't generate thumbnail if no resizing is to take place.
    if original_width == requested_width and original_height == requested_height:
        return Thumbnail(image.name, image.storage)
    # Generate the thumbnail filename.
    image_folder, image_name = os.path.split(image.name)
    image_folder = image_folder.replace("/", "-")
    thumbnail_name = "thumbnails/%s-%sx%s/%s/%s" % (generation_method, requested_width, requested_height, image_folder, image_name)
    thumbnail_path = storage.path(thumbnail_name)
    # See if the thumbnail has already been created.
    if storage.exists(thumbnail_name):
        image_timestamp = os.stat(image_path).st_mtime
        thumbnail_timestamp = os.stat(thumbnail_path).st_mtime
        # If the thumbnail is newer than the file, no more generation needs to take place.
        if thumbnail_timestamp > image_timestamp:
            return Thumbnail(thumbnail_name, storage)
    else:
        dirname = os.path.dirname(thumbnail_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
    # Calculate aspect ratios.
    required_aspect = float(requested_width) / float(requested_height)
    # Create an image buffer in memory.
    image_data = Image.open(image.path)
    # Generate a new thumbnail.
    try:
        if generation_method == THUMBNAIL:
            image_data.thumbnail((requested_width, requested_height), Image.ANTIALIAS)
        elif generation_method == RESIZE:
            image_data = image_data.resize((requested_width, requested_height), Image.ANTIALIAS)
        elif generation_method == CROP:
            source_width = min(original_width, int(original_height * required_aspect))
            source_height = min(original_height, int(original_width / required_aspect))
            source_x = (original_width - source_width) / 2
            source_y = (original_height - source_height) / 2
            image_data = image_data.transform((requested_width, requested_height), Image.EXTENT, (source_x, source_y, source_x + source_width, source_y + source_height), Image.BICUBIC)
        else:
            raise ValueError, "Unknown thumbnail generation method: %r" % generation_method
    except SyntaxError, ex:
        # HACK: The PIL will raise a SyntaxError if it encounters a 'broken png'. 
        raise IOError, str(ex)
    # Save the thumbnail to disk.
    image_data.save(thumbnail_path)
    # Return the new image object.
    return Thumbnail(thumbnail_name, storage)
    
    
def thumbnail(image, requested_width, requested_height):
    """Generates a resized thumbnail, preserving aspect ratio."""
    return generate(image, requested_width, requested_height, THUMBNAIL)
    
    
def resize(image, requested_width, requested_height):
    """Generates a rescaled thumbnail, ignoring aspect ratio."""
    return generate(image, requested_width, requested_height, RESIZE)


def crop(image, requested_width, requested_height):
    """Generates a cropped thumbnail, preserving aspect ratio."""
    return generate(image, requested_width, requested_height, CROP)

