"""Tests for core CMS functionality."""


import os, unittest

from django.conf import settings
from django.core.files.images import ImageFile

from cms.apps.pages import thumbnails


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

