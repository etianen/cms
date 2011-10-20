"""Thumbnail generation routines."""


import os.path

from PIL import Image

from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.utils import html

from cms.core import debug


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
    return image.resize(thumbnail_image_size, Image.ANTIALIAS)

def _resize_cropped(image, image_size, thumbnail_display_size, thumbnail_image_size):
    """
    Resizes the image to fit the desired size, preserving aspect ratio by
    cropping, if required.
    """
    # Resize with nice filter.
    image_aspect = image_size.aspect
    if image_aspect > thumbnail_image_size.aspect:
        # Too wide.
        pre_cropped_size = Size(thumbnail_image_size.height * image_aspect, thumbnail_image_size.height)
    else:
        # Too tall.
        pre_cropped_size = Size(thumbnail_image_size.width, thumbnail_image_size.width / image_aspect)
    # Crop.
    image = image.resize(pre_cropped_size, Image.ANTIALIAS)
    source_x = (pre_cropped_size.width - thumbnail_image_size.width) / 2
    source_y = (pre_cropped_size.height - thumbnail_image_size.height) / 2
    return image.crop((
        source_x,
        source_y,
        source_x + thumbnail_image_size.width,
        source_y + thumbnail_image_size.height,
    ))


# Methods of generating thumbnails.

PROPORTIONAL = "proportional"
RESIZED = "resized"
CROPPED = "cropped"

_methods = {PROPORTIONAL: (_size_proportional, _size, _resize, "resized"),
            RESIZED: (_size, _size, _resize, "resized"),
            CROPPED: (_size, _size_proportional, _resize_cropped, "cropped")}


class StaticFile(object):
    
    """A static file reference to be passed to the thumbnail generator."""
    
    def __init__(self, name):
        self.name = name
        self.path = os.path.join(settings.STATIC_ROOT, name)
        
    @property
    def url(self):
        stored_name = copy_to_storage(self)
        return default_storage.url(stored_name)


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
    
    
# Cache of image size information, used to cut down massively on disk hits.
_size_cache = {}

# Cache of created thumbnails, used to remove stats for thumbnails.
_created_thumbnails = set()


def copy_to_storage(image, storage=default_storage):
    """
    Copies the given image to the given storage under a thumbnails originals prefix.
    
    This method will not override the image at the destination if present.
    The new name of the file is returned.
    """
    thumbnail_name = u"thumbnails/originals/{image_name}".format(image_name=image.name)
    if not image.path in _created_thumbnails:
        if not storage.exists(thumbnail_name):
            thumbnail_name = storage.save(thumbnail_name, File(open(image.path, "rb")))
        _created_thumbnails.add(image.path)
    return thumbnail_name


def _load_once(path):
    """
    Loads the image on the first call to next, further calls to next return
    the same image.
    """
    image_data = Image.open(path)
    while True:
        yield image_data
    

def create(image, width, height, method=PROPORTIONAL, storage=default_storage):
    """
    Creates a thumbnail from the given image.
    
    If the image file is missing or corrupted, then an IOError is raised.
    """
    # Load the image data.
    image_loader = _load_once(image.path)
    # Get the desired generation method.
    try:
        display_size_callback, image_size_callback, resize_callback, folder = _methods[method]
    except KeyError:
        raise ValueError, "'%s' is not a valid thumbnail generation method. Accepted methods are: %s" % (method, ", ".join(_methods.iterkeys()))
    # Look up the image size.
    try:
        image_size = _size_cache[image.path]
    except KeyError:
        image_size = Size(*image_loader.next().size)
        _size_cache[image.path] = image_size
    # Calculate the final width and height of the thumbnail.
    thumbnail_display_size = display_size_callback(image_size, Size(width, height))
    thumbnail_image_size = image_size_callback(thumbnail_display_size, thumbnail_display_size.intersect(image_size))
    # Get the image name.
    if os.path.isabs(image.name):
        if image.name.startswith(settings.MEDIA_ROOT):
            image_name = os.path.relpath(image.name, settings.MEDIA_ROOT)
        else:
            if image.name.startswith(settings.STATIC_ROOT):
                image_name = os.path.relpath(image.name, settings.STATIC_ROOT)
            else:
                raise IOError("%s is outside of the site's MEDIA_ROOT and STATIC_ROOT." % image.name)
    else:
        image_name = image.name
    # If the file data and thumbnail data are identical, don't bother making a thumbnail.
    if image_size == thumbnail_image_size:
        if image.url:
            thumbnail_name = image_name
            thumbnail_path = image.path
            thumbnail_url = image.url
        else:
            # The image does not have a URL, so copy it into the storage.
            thumbnail_name = copy_to_storage(image, storage)
            thumbnail_path = storage.path(thumbnail_name)
            thumbnail_url = storage.url(thumbnail_name)
    else:
        # Calculate the various file paths.
        thumbnail_name = u"thumbnails/%s/%s/%s" % (folder, thumbnail_image_size, image_name)
        thumbnail_path = storage.path(thumbnail_name)
        thumbnail_url = storage.url(thumbnail_name)
        # If we need to generate the thumbnail, then generate it!
        if not thumbnail_path in _created_thumbnails:
            if os.path.exists(thumbnail_path):
                _created_thumbnails.add(thumbnail_path)
            else:
                # Make any intermediate directories.
                try:
                    os.makedirs(os.path.dirname(thumbnail_path))
                except OSError:
                    pass
                # Load the image data.
                image_data = image_loader.next()
                # Use efficient image loading if this would be sensible.
                if image_size.width < thumbnail_image_size.width and image_size.height < thumbnail_image_size.height:
                    image_data.draft(None, thumbnail_image_size)
                    image_size = Size(*image_data.size)
                # Resize the image data.
                try:
                    thumbnail_image = resize_callback(image_data, image_size, thumbnail_display_size, thumbnail_image_size)
                except Exception as ex:  # HACK: PIL can raise all sorts of wierd errors.
                    debug.print_current_exc()
                    raise IOError(str(ex))
                # Save the thumbnail.
                try:
                    thumbnail_image.save(thumbnail_path)
                except Exception as ex:  # pylint: disable=W0703
                    debug.print_current_exc()
                    try:
                        raise IOError(str(ex))
                    finally:
                        # Remove an incomplete file, if present.
                        try:
                            os.unlink(thumbnail_path)
                        except:  # pylint: disable=W0702
                            pass
                _created_thumbnails.add(thumbnail_path)
    # Return the thumbnail object.
    return Thumbnail(thumbnail_name, thumbnail_path, thumbnail_url, thumbnail_display_size, thumbnail_image_size)

