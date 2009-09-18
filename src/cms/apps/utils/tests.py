"""Unit tests for the various CMS utilities."""


import unittest

from cms.apps.utils import remote


OK_URL = "http://www.etianen.com/"

MISSING_URL = "http://www.etianen.com/foo/bar"


class RemoteTest(unittest.TestCase):
    
    """Tests that remote libraries work."""
    
    def testGetRequest(self):
        """Tests that a vanilla GET request works."""
        response = remote.open(OK_URL)
        self.assertEqual(response.status, 200)
        
    def testBrokenLink(self):
        """Tests that broken links are handled correctly."""
        # The first method should raise an error.
        try:
            remote.open(MISSING_URL)
        except remote.HttpError, ex:
            self.assertEqual(ex.code, 404)
        # The second method should return an error response.
        response = remote.open(MISSING_URL)
        self.assertEqual(response.code, 404)
        
    def testForceGet(self):
        """Tests that data can be sent using GET."""
        response = remote.open("http://www.girton.cam.ac.uk/news/", {"page": 2}, method=remote.GET)
        self.assertEqual(response.code, 200)
        
    