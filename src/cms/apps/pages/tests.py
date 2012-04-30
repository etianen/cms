"""Tests for the pages app."""

from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from cms import externals
from cms.apps.pages.models import Page, ContentBase


class TestPageContent(ContentBase):
    
    class Meta:
        app_label = "pages"


class PageEfficiencyTest(TestCase):
    
    def setUp(self):
        with externals.watson.context_manager("update_index")():
            content_type = ContentType.objects.get_for_model(TestPageContent)
            self.homepage = Page.objects.create(
                title = "Homepage",
                content_type = content_type,
            )
            TestPageContent.objects.create(
                page = self.homepage,
            )
            self.section = Page.objects.create(
                parent = self.homepage,
                title = "Section",
                content_type = content_type,
            )
            TestPageContent.objects.create(
                page = self.section,
            )
            self.subsection = Page.objects.create(
                parent = self.section,
                title = "Subsection",
                content_type = content_type,
            )
            TestPageContent.objects.create(
                page = self.subsection,
            )
            self.subsubsection = Page.objects.create(
                parent = self.subsection,
                title = "Subsubsection",
                content_type = content_type,
            )
            TestPageContent.objects.create(
                page = self.subsubsection,
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