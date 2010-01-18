"""Unit tests for the various CMS utilities."""


import os

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.core.files.images import ImageFile
from django.test.testcases import TestCase

from cms.apps.pages import permalinks, thumbnails


class TestPermalinks(TestCase):
    
    """Tests the permalinks module."""
    
    def setUp(self):
        """Sets up the test case."""
        self.user = User.objects.create(username="foo", password="foo")
    
    def testPermalinks(self):
        """
        Tests that a permalink can be created as resolved back to the original
        object.
        """
        # Test that a permalink is created correctly.
        permalink = permalinks.create(self.user)
        self.assertEqual(permalink, urlresolvers.reverse("permalink_redirect", kwargs={"content_type_id": ContentType.objects.get_for_model(User).id,
                                                                                       "object_id": self.user.id}))
        # Test that a permalink is resolved correctly.
        user = permalinks.resolve(permalink)
        self.assertEqual(user, self.user)
        # Tests that a permalink is expanded correctly.
        self.assertEqual(permalinks.expand(permalink), user.get_absolute_url())
        # Tests that HTML attribute expansion works correctly.
        html = '<a href="%(link)s"/><img src="%(link)s"/>'
        before_expand_html = html % {"link": permalink}
        after_expand_html = html % {"link": user.get_absolute_url()}
        self.assertEqual(after_expand_html, permalinks.expand_links_html(before_expand_html))
        
    def tearDown(self):
        """Destroys the test case."""
        self.user.delete()
        
        
class TestThumbnails(TestCase):
    
    """Tests the thumbnails module."""
    
    def setUp(self):
        """Sets up the test case."""
        self.image = ImageFile(open(os.path.join(settings.CMS_ROOT, "media", "img", "content-types", "content.png")))
        self.image.path = self.image.name
        self.original_width = self.image.width
        self.original_height = self.image.height
    
    def testProportionalThumbnail(self):
        """Tests the proportional thumbnail resize."""
        target_width = int(self.original_width / 2)
        target_height = int(self.original_height / 2)
        # Test a resize limited by width.
        thumbnail = thumbnails.create(self.image, target_width, 100000, thumbnails.PROPORTIONAL)
        self.assertEqual(thumbnail.width, target_width)
        self.assertEqual(thumbnail.height, target_height)
        # Test a resize limited by height.
        thumbnail = thumbnails.create(self.image, 1000000, target_height, thumbnails.PROPORTIONAL)
        self.assertEqual(thumbnail.width, target_width)
        self.assertEqual(thumbnail.height, target_height)
        
    def testResizedThumbnail(self):
        """Tests the resizing thumbnail resize."""
        target_width = int(self.original_width / 2)
        target_height = int(self.original_height / 4)
        thumbnail = thumbnails.create(self.image, target_width, target_height, thumbnails.RESIZED)
        self.assertEqual(thumbnail.width, target_width)
        self.assertEqual(thumbnail.height, target_height)
        
    def testCroppedThumbnail(self):
        """Tests the cropping thumbnail resize."""
        target_width = int(self.original_width / 2)
        target_height = int(self.original_height / 4)
        thumbnail = thumbnails.create(self.image, target_width, target_height, thumbnails.CROPPED)
        self.assertEqual(thumbnail.width, target_width)
        self.assertEqual(thumbnail.height, target_height)
        
        