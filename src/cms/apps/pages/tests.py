"""Tests for core CMS functionality."""


import datetime, os, unittest

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files.images import ImageFile

from cms.apps.pages import thumbnails
from cms.apps.pages.optimizations import cached_getter, cached_setter, cached_deleter


# Test thumbnail generation.


class ThumbnailGenerationTest(unittest.TestCase):
    
    """Tests the thumbnail generation utilities."""
    
    def setUp(self):
        """Initializes a test image."""
        image_path = os.path.join(settings.CMS_MEDIA_ROOT, "img", "etianen.png")
        image_file = open(image_path)
        image = ImageFile(image_file)
        image.path = image_path
        self.image = image
        
    def deleteThumbnail(self, thumbnail):
        """Deletes a temporary thumbnail file."""
        os.remove(thumbnail.path)
        
    def testGenerateThumbnail(self):
        """Tests that the basic thumbnail generation works."""
        narrow_thumbnail = thumbnails.thumbnail(self.image, 10, 1000)
        self.assertTrue(narrow_thumbnail.url, "Thumbnail does not have a valid URL.")
        self.assertTrue(narrow_thumbnail.path, "Thumbnail does not have a valid path.")
        self.assertEqual(narrow_thumbnail.width, 10)
        self.deleteThumbnail(narrow_thumbnail)
        short_thumbnail = thumbnails.thumbnail(self.image, 1000, 10)
        self.assertEqual(short_thumbnail.height, 10)
        self.deleteThumbnail(short_thumbnail)

    def testGenerateResizedThumbnail(self):
        """Tests that resized thumbnails can be generated."""
        resized_thumbnail = thumbnails.resize(self.image, 5, 8)
        self.assertEqual(resized_thumbnail.width, 5)
        self.assertEqual(resized_thumbnail.height, 8)
        self.deleteThumbnail(resized_thumbnail)
        
    def testGenerateCroppedThumbnail(self):
        """Tests that cropped thumbnails can be generated."""
        cropped_thumbnail = thumbnails.crop(self.image, 5, 8)
        self.assertEqual(cropped_thumbnail.width, 5)
        self.assertEqual(cropped_thumbnail.height, 8)
        self.deleteThumbnail(cropped_thumbnail)


# Test the optimizations.


class CachedPropertyTest(object):
    
    """Used to test the cached_property optimization."""
    
    def __init__(self):
        self.call_count = 0
        self._value = "initial"
        
    @cached_getter
    def get_value(self):
        self.call_count += 1
        return self._value
    
    @cached_setter(get_value)
    def set_value(self, value):
        self._value = value
        
    @cached_deleter(get_value)
    def del_value(self):
        del self._value
        
    
class TestCachedProperty(unittest.TestCase):
    
    """Tests the cached_property optimization."""
    
    def setUp(self):
        """Sets up a CachedPropertyTest object."""
        self.cached_property_test = CachedPropertyTest()
    
    def testGetterIsCached(self):
        """Tests that calls to getters are cached."""
        self.cached_property_test.get_value()
        self.assertEqual(self.cached_property_test.call_count, 1)
        self.cached_property_test.get_value()
        self.assertEqual(self.cached_property_test.call_count, 1)
        
    def testSetterSetsCache(self):
        """Tests that calls to setters sets the cache."""
        self.cached_property_test.set_value("changed")
        self.assertEqual(self.cached_property_test.get_value(), "changed")
        self.assertEqual(self.cached_property_test.call_count, 0)
        
    def testDeleterClearsCache(self):
        """Tests that calls to deleters clear the cache."""
        self.cached_property_test.get_value()
        self.cached_property_test.del_value()
        self.assertRaises(AttributeError, lambda: self.cached_property_test.get_value())
        self.cached_property_test.set_value("changed")
        self.assertEqual(self.cached_property_test.call_count, 2)
        
