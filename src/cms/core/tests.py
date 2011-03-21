"""Unit tests for the various CMS utilities."""


from __future__ import with_statement

import os, time

from django import template
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.core.files.storage import default_storage
from django.test.testcases import TestCase

from cms.core import permalinks, thumbnails, optimizations


class TestCachedPropertyDummy(object):
    
    """Dummy object for testing the cached property optimization."""
    
    def __init__(self):
        self.getter_calls = 0
        self._attr = "Foo"
    
    @optimizations.cached_getter
    def get_attr(self):
        self.getter_calls += 1
        return self._attr
    
    @optimizations.cached_setter(get_attr)
    def set_attr(self, value):
        self._attr = value
        
    @optimizations.cached_deleter(get_attr)
    def del_attr(self):
        del self._attr

    attr = property(get_attr,
                    set_attr,
                    del_attr)


class TestOptimizations(TestCase):
    
    """Tests that the CMS optimizations module works."""
    
    def testCachedProperty(self):
        """Tests the cached property decorators."""
        dummy = TestCachedPropertyDummy()
        # Test that the cache initializes.
        self.assertEqual(dummy.attr, "Foo")
        self.assertEqual(dummy.getter_calls, 1)
        self.assertEqual(dummy.attr, "Foo")
        self.assertEqual(dummy.getter_calls, 1)
        # Test that the cache is updated.
        dummy.attr = "Bar"
        self.assertEqual(dummy.attr, "Bar")
        self.assertEqual(dummy.getter_calls, 1)
        # Test that the cache is deleted.
        del dummy.attr
        self.assertRaises(AttributeError, lambda: dummy.attr)
        self.assertEqual(dummy.getter_calls, 2)
        # Test that the property can be re-set.
        dummy.attr = "Baz"
        self.assertEqual(dummy.attr, "Baz")
        self.assertEqual(dummy.getter_calls, 2)
        

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
        
    def tearDown(self):
        """Destroys the test case."""
        self.user.delete()
        
        
# Create a dummy file object for testing thumbnail generation.
DUMMY_IMAGE_NAME = "img/python-powered.png"
DUMMY_IMAGE_PATH = "/".join((settings.CMS_ROOT, "media", DUMMY_IMAGE_NAME))
DUMMY_IMAGE_URL = "/".join((settings.STATIC_URL, DUMMY_IMAGE_NAME))
DUMMY_IMAGE = thumbnails.Thumbnail(DUMMY_IMAGE_NAME, DUMMY_IMAGE_PATH, DUMMY_IMAGE_URL, thumbnails.Size(200, 80))


def unlink_tmp_file(path):
    """Unlinks the given file, provided it isn't the dummy file."""
    if path != DUMMY_IMAGE_PATH:
        os.unlink(path)


class TestThumbnails(TestCase):
    
    """Tests the thumbnails module."""
    
    def testThumbnail(self):
        """Tests the thumbnail generation method."""
        thumbnail_size = DUMMY_IMAGE.display_size.scale(0.5, 0.5)
        # Test that the thumbnail can be too wide.
        thumbnail = thumbnails.create(DUMMY_IMAGE, thumbnail_size.width * 1.5, thumbnail_size.height, thumbnails.PROPORTIONAL)
        try:
            self.assertEqual(thumbnail.display_size, thumbnail_size)
            self.assertEqual(thumbnail.display_size, thumbnail.image_size)
            self.assertNotEqual(thumbnail.path, DUMMY_IMAGE.path)
        finally:
            unlink_tmp_file(thumbnail.path)
        # Test that the thumbnail can be too tall.
        thumbnail = thumbnails.create(DUMMY_IMAGE, thumbnail_size.width, thumbnail_size.height * 1.5, thumbnails.PROPORTIONAL)
        try:
            self.assertEqual(thumbnail.display_size, thumbnail_size)
            self.assertEqual(thumbnail.display_size, thumbnail.image_size)
            self.assertNotEqual(thumbnail.path, DUMMY_IMAGE.path)
        finally:
            unlink_tmp_file(thumbnail.path)
        # Test that a massive thumbnail can be generated with the required aspect ratio, but no extra data.
        thumbnail_size = DUMMY_IMAGE.display_size.scale(2, 2)
        thumbnail = thumbnails.create(DUMMY_IMAGE, thumbnail_size.width, thumbnail_size.height * 1.5, thumbnails.PROPORTIONAL)
        try:
            self.assertEqual(thumbnail.display_size, thumbnail_size)
            self.assertEqual(DUMMY_IMAGE.display_size, thumbnail.image_size)
            self.assertEqual(thumbnail.path, DUMMY_IMAGE.path)
        finally:
            unlink_tmp_file(thumbnail.path)
    
    def testResize(self):
        """Tests the resize generation method."""
        thumbnail_size = DUMMY_IMAGE.display_size.scale(1, 0.5)
        # Generate the thumbnail.
        thumbnail = thumbnails.create(DUMMY_IMAGE, thumbnail_size.width, thumbnail_size.height, thumbnails.RESIZED)
        try:
            self.assertEqual(thumbnail.display_size, thumbnail_size)
            self.assertEqual(thumbnail.display_size, thumbnail.image_size)
            self.assertNotEqual(thumbnail.path, DUMMY_IMAGE.path)
        finally:
            unlink_tmp_file(thumbnail.path)
        # Test that a massive thumbnail can be generated with the required aspect ratio, but no extra data.
        thumbnail_size = DUMMY_IMAGE.display_size.scale(2, 3)
        thumbnail = thumbnails.create(DUMMY_IMAGE, thumbnail_size.width, thumbnail_size.height, thumbnails.RESIZED)
        try:
            self.assertEqual(thumbnail.display_size, thumbnail_size)
            self.assertEqual(DUMMY_IMAGE.display_size, thumbnail.image_size)
            self.assertEqual(thumbnail.path, DUMMY_IMAGE.path)
        finally:
            unlink_tmp_file(thumbnail.path)
        
    def testCrop(self):
        """Tests the crop generation method."""
        # Test that the thumbnail can be too wide.
        thumbnail_size = DUMMY_IMAGE.display_size.scale(0.66, 0.5)
        thumbnail = thumbnails.create(DUMMY_IMAGE, thumbnail_size.width, thumbnail_size.height, thumbnails.CROPPED)
        try:
            self.assertEqual(thumbnail.display_size, thumbnail_size)
            self.assertEqual(thumbnail.display_size, thumbnail.image_size)
            self.assertNotEqual(thumbnail.path, DUMMY_IMAGE.path)
        finally:
            unlink_tmp_file(thumbnail.path)
        # Test that the thumbnail can be too tall.
        thumbnail_size = DUMMY_IMAGE.display_size.scale(0.5, 0.66)
        thumbnail = thumbnails.create(DUMMY_IMAGE, thumbnail_size.width, thumbnail_size.height, thumbnails.CROPPED)
        try:
            self.assertEqual(thumbnail.display_size, thumbnail_size)
            self.assertEqual(thumbnail.display_size, thumbnail.image_size)
            self.assertNotEqual(thumbnail.path, DUMMY_IMAGE.path)
        finally:
            unlink_tmp_file(thumbnail.path)
        # Test that a massive thumbnail can be generated with the required aspect ratio, but no extra data.
        thumbnail_size = DUMMY_IMAGE.display_size.scale(2, 4)
        thumbnail = thumbnails.create(DUMMY_IMAGE, thumbnail_size.width, thumbnail_size.height, thumbnails.CROPPED)
        try:
            self.assertEqual(thumbnail.display_size, thumbnail_size)
            self.assertEqual(thumbnail.image_size.aspect, thumbnail.display_size.aspect)
            self.assertNotEqual(thumbnail.path, DUMMY_IMAGE.path)
        finally:
            unlink_tmp_file(thumbnail.path)
        
    def testCache(self):
        """Tests that thumbnails are cached on disk."""
        thumbnail_size = DUMMY_IMAGE.display_size.scale(0.5, 0.5)
        thumbnail = thumbnails.create(DUMMY_IMAGE, thumbnail_size.width, thumbnail_size.height)
        st_mtime = os.stat(thumbnail.path).st_mtime
        # On FAT32 systems, the resolution is only 2 seconds.
        time.sleep(2)
        thumbnail = thumbnails.create(DUMMY_IMAGE, thumbnail_size.width, thumbnail_size.height)
        self.assertEqual(st_mtime, os.stat(thumbnail.path).st_mtime)
        
    def testExceptions(self):
        """Tests that the correct exceptions are returned."""
        # Test that a missing image raises an IOError.
        INVALID_PATH = "/foo/bar"
        INVALID_IMAGE = thumbnails.Thumbnail("bar", INVALID_PATH, "/foo/bar/", thumbnails.Size(50, 50))
        self.assertFalse(os.path.exists(INVALID_PATH))
        self.assertRaises(IOError, lambda: thumbnails.create(INVALID_IMAGE, 20, 20))
        # Test that a garbage image raises an IOError.
        GARBAGE_PATH = default_storage.path("garbage.png")
        with open(GARBAGE_PATH, "wb") as garbage_file:
            garbage_file.write("foobar")
        GARBAGE_IMAGE = thumbnails.Thumbnail("garbage.png", GARBAGE_PATH, "/media/garbage.png", thumbnails.Size(50, 50))
        self.assertRaises(IOError, lambda: thumbnails.create(GARBAGE_IMAGE, 20, 20))
        unlink_tmp_file(GARBAGE_PATH)
        
    def testUnicodeConversion(self):
        """Tests that the image tag can output a unicode representation."""
        image_tag = u'<img src="%s" width="%i" height="%i" alt=""/>' % (DUMMY_IMAGE_URL, DUMMY_IMAGE.display_size.width, DUMMY_IMAGE.display_size.height)
        self.assertEqual(unicode(DUMMY_IMAGE), image_tag)
        self.assertEqual(str(DUMMY_IMAGE), str(image_tag))
        
    def testThumbnailTag(self):
        """Tests the thumbnail generation tag."""
        target_size = DUMMY_IMAGE.display_size.scale(0.5, 0.25)
        thumbnail_proportional = thumbnails.create(DUMMY_IMAGE, target_size.width, target_size.height, thumbnails.PROPORTIONAL)
        thumbnail_resized = thumbnails.create(DUMMY_IMAGE, target_size.width, target_size.height, thumbnails.RESIZED)
        thumbnail_cropped = thumbnails.create(DUMMY_IMAGE, target_size.width, target_size.height, thumbnails.CROPPED)
        template_src = """{% load thumbnails %}
        {% thumbnail image width height %}
        {% thumbnail image width height proportional %}
        {% thumbnail image width height resized %}
        {% thumbnail image width height cropped %}
        {% thumbnail image width height as thumbnail %}<img src="{{thumbnail.url}}" width="{{thumbnail.width}}" height="{{thumbnail.height}}" alt=""/>
        {% thumbnail image width height proportional as thumbnail %}<img src="{{thumbnail.url}}" width="{{thumbnail.width}}" height="{{thumbnail.height}}" alt=""/>
        """
        expected_html = """
        <img src="%(proportional_src)s" width="%(proportional_width)s" height="%(proportional_height)s" alt=""/>
        <img src="%(proportional_src)s" width="%(proportional_width)s" height="%(proportional_height)s" alt=""/>
        <img src="%(resized_src)s" width="%(target_width)s" height="%(target_height)s" alt=""/>
        <img src="%(cropped_src)s" width="%(target_width)s" height="%(target_height)s" alt=""/>
        <img src="%(proportional_src)s" width="%(proportional_width)s" height="%(proportional_height)s" alt=""/>
        <img src="%(proportional_src)s" width="%(proportional_width)s" height="%(proportional_height)s" alt=""/>
        """ % {"proportional_src": thumbnail_proportional.url,
               "proportional_width": thumbnail_proportional.width,
               "proportional_height": thumbnail_proportional.height,
               "resized_src": thumbnail_resized.url,
               "cropped_src": thumbnail_cropped.url,
               "target_width": target_size.width,
               "target_height": target_size.height}
        context = {"image": DUMMY_IMAGE,
                   "width": target_size.width,
                   "height": target_size.height}
        self.assertEqual(expected_html, template.Template(template_src).render(template.Context(context)))    