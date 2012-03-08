"""Tests for the pages app."""

from django.test import TestCase

from cms.apps.pages.models import Page


class PageEfficiencyTest(TestCase):
    
    def setUp(self):
        self.homepage = Page.objects.create(
            title = "Homepage",
            order = 1,
            content_type_id = 1,
        )
        self.section = Page.objects.create(
            parent = self.homepage,
            title = "Section",
            order = 2,
            content_type_id = 1,
        )
        self.subsection = Page.objects.create(
            parent = self.section,
            title = "Subsection",
            order = 3,
            content_type_id = 1,
        )
        
    def testChildPrefetching(self):
        with self.assertNumQueries(3):
            homepage = Page.objects.get_homepage()
        with self.assertNumQueries(0):
            subsection = homepage.children.all()[0].children.all()[0]
        self.assertEqual(subsection.title, "Subsection")
        with self.assertNumQueries(0):
            subsection = homepage.navigation[0].navigation[0]
        self.assertEqual(subsection.title, "Subsection")