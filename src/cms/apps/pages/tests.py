"""Tests for the pages app."""

from django.test import TestCase

from cms.apps.pages.models import Page


class PageEfficiencyTest(TestCase):
    
    def setUp(self):
        self.homepage = Page.objects.create(
            title = "Homepage",
            content_type_id = 1,
        )
        self.section = Page.objects.create(
            parent = self.homepage,
            title = "Section",
            content_type_id = 1,
        )
        self.subsection = Page.objects.create(
            parent = self.section,
            title = "Subsection",
            content_type_id = 1,
        )
        self.subsubsection = Page.objects.create(
            parent = self.subsection,
            title = "Subsubsection",
            content_type_id = 1,
        )
        
    def testChildPrefetching(self):
        # Make sure that prefetching works to two levels deep.
        with self.assertNumQueries(3):
            homepage = Page.objects.get_homepage()
        with self.assertNumQueries(0):
            subsection = homepage.children[0].children[0]
        self.assertEqual(subsection.title, "Subsection")
        with self.assertNumQueries(0):
            subsection = homepage.navigation[0].navigation[0]
        self.assertEqual(subsection.title, "Subsection")
        # Make sure that, beyond this, it doesn't go  pathalogical.
        with self.assertNumQueries(1):
            subsubsection = subsection.children[0]
        self.assertEqual(subsubsection.title, "Subsubsection")
        with self.assertNumQueries(0):
            subsubsection = subsection.children[0]
        self.assertEqual(subsubsection.title, "Subsubsection")