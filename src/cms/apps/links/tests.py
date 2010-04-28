"""Tests for the links application."""


from django.test.testcases import TestCase
from django.test.client import Client

from cms.apps.pages.tests import make_test_page
from cms.apps.links.content import Link


TEST_REDIRECT_URL = "http://www.djangoproject.com"


class TestRedirectContent(TestCase):
    
    """Tests the redirect content class."""
    
    def setUp(self):
        """Initializes the test case."""
        self.page = make_test_page(title="Test", url_title="test", order=1, content_type=Link.registration_key, content_data={"link_url": TEST_REDIRECT_URL})
    
    def testIndexView(self):
        """Tests the index page."""
        c = Client()
        response = c.get(self.page.get_absolute_url())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], TEST_REDIRECT_URL)
        
    def tearDown(self):
        """Destroys the test case."""
        self.page.delete()
        
        