from django.test import TestCase

from cms.models.fields import resolve_link, LinkResolutionError


class TestLinkField(TestCase):
    
    def testResolveLink(self):
        self.assertEqual(resolve_link("http://www.example.com/foo/"), "http://www.example.com/foo/")
        self.assertEqual(resolve_link("www.example.com/foo/"), "http://www.example.com/foo/")
        self.assertEqual(resolve_link("www.example.com"), "http://www.example.com/")
        self.assertEqual(resolve_link("/foo/"), "/foo/")
        self.assertRaises(LinkResolutionError, lambda: resolve_link("foo/"))