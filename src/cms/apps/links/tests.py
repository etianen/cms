from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from cms.apps.pages.models import Page
from cms.apps.links.models import Link


class TestLinks(TestCase):
    
    def setUp(self):
        page = Page.objects.create(
            title = "Homepage",
            content_type = ContentType.objects.get_for_model(Link),
        )
        Link.objects.create(
            page = page,
            link_url = "http://www.example.com/",
        )
    
    def testLinkRedirect(self):
        response = self.client.get("/")
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response["Location"], "http://www.example.com/")