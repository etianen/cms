"""Thumbnail generation routines."""


import os

from PIL import Image  #@UnresolvedImport

from django.core.files.storage import default_storage
from django.utils import html


__all__ = ("create", "PROPORTIONAL", "RESIZED", "CROPPED",)


class Size(tuple):

    """Represents the size of an image."""
    
    __slots__ = ()
    
    def __new__(cls, width, height):
        """Creats a new Size."""
        return tuple.__new__(cls, (int(width), int(height)))
    
    @property
    def width(self):
        return self[0]
    
    @property
    def height(self):
        return self[1]
    
    @property
    def aspect(self):
        """Returns the aspect ratio of this size."""
        return float(self.width) / float(self.height)
    
    def intersect(self, size):
        """
        Returns a Size that represents the intersection of this and another
        Size.
        """
        return Size(min(self.width, size.width), min(self.height, size.height))
    
    def constrain(self, reference):
        """
        Returns a new Size that is this Size shrunk to fit inside.
        """
        reference_aspect = reference.aspect
        width = min(round(self.height * reference_aspect), self.width)
        height = min(round(self.width / reference_aspect), self.height)
        return Size(width, height)
    
    def scale(self, x_scale, y_scale):
        """Returns a new Size with it's width and height scaled."""
        return Size(float(self.width) * x_scale, float(self.height) * y_scale)
    
    def __str__(self):
        """Returns a string representation of this Size."""
        return "%ix%i" % (self.width, self.height)


# Size adjustment callbacks. These are used to determine the display and data size of the thumbnail.

def _size(reference, size):
    """Ignores the reference size, and just returns the desired size."""
    return size

def _size_proportional(reference, size):
    """Adjusts the desired size to match the aspect ratio of the reference."""
    return size.constrain(reference)


# Resize callbacks. These are used to actually resize the image data.

def _resize(image, image_size, thumbnail_display_size, thumbnail_image_size):
    """
    Resizes the image to exactly match the desired data size, ignoring aspect
    ratio.
    """
    return image.resize((thumbnail_image_size), Image.ANTIALIAS)

def _resize_cropped(image, image_size, thumbnail_display_size, thumbnail_image_size):
    """
    Resizes the image to fit the desired size, preserving aspect ratio by
    cropping, if required.
    """
    source_size = image_size.constrain(thumbnail_display_size)
    source_x = (image_size.width - source_size.width) / 2
    source_y = (image_size.height - source_size.height) / 2
    return image.transform(thumbnail_image_size, Image.EXTENT, (source_x, source_y, source_x + source_size.width, source_y + source_size.height), Image.BICUBIC)


# Methods of generating thumbnails.

PROPORTIONAL = "proportional"
RESIZED = "resized"
CROPPED = "cropped"

_methods = {PROPORTIONAL: (_size_proportional, _size, _resize, "resized"),
            RESIZED: (_size, _size, _resize, "resized"),
            CROPPED: (_size, _size_proportional, _resize_cropped, "cropped")}


class Thumbnail(object):
    
    """Efficient data structure for holding generated thumbnail data."""
    
    __slots__ = ("name", "path", "url", "display_size", "image_size",)
    
    def __init__(self, name, path, url, display_size, image_size=None):
        """Initializes the Thumbnail."""
        self.name = name
        self.path = path
        self.url = url
        self.display_size = display_size
        self.image_size = image_size or display_size
        
    @property
    def width(self):
        """Returns the width of the thumbnail."""
        return self.display_size.width
    
    @property
    def height(self):
        """Returns the height of the thumbnail."""
        return self.display_size.height
    
    def __unicode__(self):
        """Returns the thumbnail as a XHTML image tag."""
        return u'<img src="%s" width="%i" height="%i" alt=""/>' % (html.escape(self.url), self.width, self.height)
    
    def __str__(self):
        """Returns the thumbnail as a XHTML image tag."""
        return str(unicode(self))
    

def create(image, width, height, method=PROPORTIONAL, storage=default_storage):
    """
    Creates a thumbnail from the given image.
    
    If the image file is missing or corrupted, then an IOError is raised.
    """
    # Load the image data.
    image_data = Image.open(image.path)
    # Get the desired generation method.
    try:
        display_size_callback, image_size_callback, resize_callback, folder = _methods[method]
    except KeyError:
        raise ValueError, "'%' is not a valid thumbnail generation method. Accepted methods are: %s" % (method, ", ".join(_methods.iterkeys()))
    # Calculate the final width and height of the thumbnail.
    image_size = Size(*image_data.size)
    thumbnail_display_size = display_size_callback(image_size, Size(width, height))
    thumbnail_image_size = image_size_callback(thumbnail_display_size, thumbnail_display_size.intersect(image_size))
    # If the file data and thumbnail data are identical, don't bother making a thumbnail.
    if image_size == thumbnail_image_size:
        thumbnail_name = image.name
        thumbnail_path = image.path
    else:
        # Calculate the various file paths.
        thumbnail_name = "thumbnails/%s/%s/%s" % (folder, thumbnail_image_size, image.name)
        thumbnail_path = storage.path(thumbnail_name)
        # Make any intermediate directories.
        try:
            os.makedirs(os.path.dirname(thumbnail_path))
        except OSError:
            pass
        # Check whether the thumbnail exists, and is more recent than the image.
        image_timestamp = os.stat(image.path).st_mtime 
        try:
            thumbnail_timestamp = os.stat(thumbnail_path).st_mtime
        except OSError:
            # The thumbnail does not exist, so we need to generate it.
            generation_required = True
        else:
            generation_required = image_timestamp > thumbnail_timestamp
        # If we need to generate the thumbnail, then generate it!
        if generation_required:
            # Use efficient image loading if this would be sensible.
            if image_size.width < thumbnail_image_size.width and image_size.height < thumbnail_image_size.height:
                image_data.draft(None, thumbnail_image_size)
                image_size = Size(*image_data.size)
            # Resize the image data.
            try:
                thumbnail_image = resize_callback(image_data, image_size, thumbnail_display_size, thumbnail_image_size)
            except SyntaxError, ex:
                # HACK: The PIL will raise a SyntaxError if it encounters a 'broken png'. 
                raise IOError, str(ex)
            # Save the thumbnail.
            try:
                thumbnail_image.save(thumbnail_path)
            except:
                # Remove an incomplete file, if present.
                try:
                    os.unlink(thumbnail_path)
                except OSError:
                    pass
                # Re-raise the original exception.
                raise
    # Return the thumbnail object.
    thumbnail_url = storage.url(thumbnail_name)
    return Thumbnail(thumbnail_name, thumbnail_path, thumbnail_url, thumbnail_display_size, thumbnail_image_size)

