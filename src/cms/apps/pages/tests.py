"""Unit tests for the various CMS utilities."""


from __future__ import with_statement

import os

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.core.files.storage import default_storage
from django.test.testcases import TestCase

from cms.apps.pages import permalinks, thumbnails
from cms.apps.media.models import File


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
        
        
TEMP_FILE_NAME = "temp.png"


class TestThumbnails(TestCase):
    
    """Tests the thumbnails module."""
    
    
    def setUp(self):
        """Sets up the test case."""
        with open(os.path.join(settings.CMS_ROOT, "media", "img", "content-types", "content.png")) as src_file:
            with open(os.path.join(settings.MEDIA_ROOT, TEMP_FILE_NAME), "wb") as dst_file:
                dst_file.write(src_file.read())
        self.file = File.objects.create(title="Test File", file=TEMP_FILE_NAME)
        self.original_width = 64
        self.original_height = 64
    
    def testProportionalThumbnail(self):
        """Tests the proportional thumbnail resize."""
        target_width = int(self.original_width / 2)
        target_height = int(self.original_height / 2)
        # Test a resize limited by width.
        thumbnail = thumbnails.create(self.file.file, target_width, 100000, thumbnails.PROPORTIONAL)
        self.assertEqual(thumbnail.width, target_width)
        self.assertEqual(thumbnail.height, target_height)
        # Test a resize limited by height.
        thumbnail = thumbnails.create(self.file.file, 1000000, target_height, thumbnails.PROPORTIONAL)
        self.assertEqual(thumbnail.width, target_width)
        self.assertEqual(thumbnail.height, target_height)
        
    def testResizedThumbnail(self):
        """Tests the resizing thumbnail resize."""
        target_width = int(self.original_width / 2)
        target_height = int(self.original_height / 4)
        thumbnail = thumbnails.create(self.file.file, target_width, target_height, thumbnails.RESIZED)
        self.assertEqual(thumbnail.width, target_width)
        self.assertEqual(thumbnail.height, target_height)
        
    def testCroppedThumbnail(self):
        """Tests the cropping thumbnail resize."""
        target_width = int(self.original_width / 2)
        target_height = int(self.original_height / 4)
        thumbnail = thumbnails.create(self.file.file, target_width, target_height, thumbnails.CROPPED)
        self.assertEqual(thumbnail.width, target_width)
        self.assertEqual(thumbnail.height, target_height)
        
    def testGenerateThumbnailsHtml(self):
        """Tests the HTML thumbnail replacement."""
        html = '<img alt="" height="%(height)s" src="%(src)s" width="%(width)s"/>'
        target_width = int(self.original_width / 2)
        target_height = int(self.original_height / 4)
        before_replace_html = html % {"src": permalinks.create(self.file), "width": target_width, "height": target_height}
        after_replace_html = html % {"src": thumbnails.create(self.file.file, target_width, target_height, thumbnails.RESIZED).url, "width": target_width, "height": target_height}
        self.assertEqual(after_replace_html, thumbnails.generate_thumbnails_html(before_replace_html))
        
    def tearDown(self):
        """Destroys the test case."""
        self.file.delete()
        default_storage.delete(TEMP_FILE_NAME)
        
        