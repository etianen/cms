"""Unit tests for the various CMS utilities."""


from django.test.testcases import TestCase

from cms.apps.utils import remote


OK_URL = "http://www.etianen.com/"

MISSING_URL = "http://www.etianen.com/foo/bar/"


class RemoteTest(TestCase):
    
    """Tests that remote libraries work."""
    
    def testGetRequest(self):
        """Tests that a vanilla GET request works."""
        response = remote.open(OK_URL)
        self.assertContains(response, "Enlightened Website Development")
        
    def testBrokenLink(self):
        """Tests that broken links are handled correctly."""
        # The first method should raise an error.
        try:
            remote.open(MISSING_URL)
        except remote.HttpError, ex:
            self.assertEqual(ex.status_code, 404)
        # The second method should return an error response.
        response = remote.open(MISSING_URL, require_success=False)
        self.assertContains(response, "Page Not Found", status_code=404)
        
    def testForceGet(self):
        """Tests that data can be sent using GET."""
        response = remote.open("http://www.girton.cam.ac.uk/news/", {"page": 2}, method=remote.GET)
        self.assertContains(response, "Page 2")
        
    def testPostRequest(self):
        """Tests that a post request can be sent."""
        response = remote.open("http://www.etianen.com/admin/", {"username": "david", "password": "password"})
        self.assertContains(response, '<p class="errornote">')
        
        