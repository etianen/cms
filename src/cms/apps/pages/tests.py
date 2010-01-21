"""Unit tests for the various CMS utilities."""


from __future__ import with_statement

import os, re

from django import template
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.core.files.storage import default_storage
from django.test.testcases import TestCase
from django.test.client import Client

from cms.apps.pages import permalinks, thumbnails, content, optimizations
from cms.apps.pages.models import Page
from cms.apps.media.models import File


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
        
    def testCreateThumbnailsHtml(self):
        """Tests the HTML thumbnail replacement."""
        html = '<img alt="" height="%(height)s" src="%(src)s" width="%(width)s"/>'
        target_width = int(self.original_width / 2)
        target_height = int(self.original_height / 4)
        before_replace_html = html % {"src": permalinks.create(self.file), "width": target_width, "height": target_height}
        after_replace_html = html % {"src": thumbnails.create(self.file.file, target_width, target_height, thumbnails.RESIZED).url, "width": target_width, "height": target_height}
        self.assertEqual(after_replace_html, thumbnails.create_thumbnails_html(before_replace_html))
        
    def testThumbnailTag(self):
        """Tests the thumbnail generation tag."""
        target_width = int(self.original_width / 2)
        target_height = int(self.original_height / 4)
        thumbnail_proportional = thumbnails.create(self.file.file, target_width, target_height, thumbnails.PROPORTIONAL)
        thumbnail_resized = thumbnails.create(self.file.file, target_width, target_height, thumbnails.RESIZED)
        thumbnail_cropped = thumbnails.create(self.file.file, target_width, target_height, thumbnails.CROPPED)
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
               "target_width": target_width,
               "target_height": target_height}
        context = {"image": self.file.file,
                   "width": target_width,
                   "height": target_height}
        self.assertEqual(expected_html, template.Template(template_src).render(template.Context(context)))
        
    def tearDown(self):
        """Destroys the test case."""
        self.file.delete()
        default_storage.delete(TEMP_FILE_NAME)
        
        
def make_test_page(**kwargs):
    """Creates a page for testing."""
    content_data = kwargs.pop("content_data", {})
    page = Page(**kwargs)
    content_obj = content.lookup(page.content_type)(page)
    for field in content_obj.fields:
        if field.name in content_data:
            setattr(content_obj, field.name, content_data[field.name])
        elif isinstance(field, content.HtmlField):
            setattr(content_obj, field.name, "foobar")
        elif isinstance(field, content.CharField):
            setattr(content_obj, field.name, "foo")
        elif isinstance(field, content.TextField):
            setattr(content_obj, field.name, "bar")
        elif isinstance(field, content.BooleanField):
            setattr(content_obj, field.name, True)
        else:
            setattr(content_obj, field.name, None)
    page.content = content_obj
    page.save()
    return page
        
       
class TestPages(TestCase):
    
    """Tests the pages models."""
    
    def setUp(self):
        """Sets up the test case."""
        # Create a test file object.
        with open(os.path.join(settings.CMS_ROOT, "media", "img", "content-types", "content.png")) as src_file:
            with open(os.path.join(settings.MEDIA_ROOT, TEMP_FILE_NAME), "wb") as dst_file:
                dst_file.write(src_file.read())
        self.file = File.objects.create(title="Test File", file=TEMP_FILE_NAME)
        # Create some dummy content.
        file_permalink = permalinks.create(self.file)
        html = u'<a href="%(link)s"/><img height="16" src="%(src)s" width="32"/>'
        self.test_html = html % {"link": file_permalink, "src": file_permalink}
        self.expanded_html = html % {"link": self.file.get_absolute_url(), "src": thumbnails.create(self.file.file, 32, 16, thumbnails.RESIZED).url}
        # Get the name of a html content area.
        for field in content.lookup("content")(None).fields:
            if isinstance(field, content.HtmlField):
                self.fieldname = field.name
        # Create some test pages.
        self.homepage = make_test_page(title="Home", url_title="home", order=1, content_type="content", content_data={self.fieldname: self.test_html})
        self.section = make_test_page(title="Section", url_title="section", parent=self.homepage, order=2, content_type="content", content_data={self.fieldname: self.test_html})
        self.subsection = make_test_page(title="SubSection", url_title="subsection", parent=self.section, order=3, content_type="content", content_data={self.fieldname: self.test_html})
        self.subsubsection = make_test_page(title="SubSubSection", url_title="subsubsection", parent=self.subsection, order=4, content_type="content", content_data={self.fieldname: self.test_html})
    
    def testIndexView(self):
        """Tests the default content index view."""
        c = Client()
        # Test the homepage.
        response = c.get(self.homepage.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        # Test the subsection.
        response = c.get(self.subsection.get_absolute_url())
        self.assertEqual(response.status_code, 200)
    
    def testHtmlFilter(self):
        """Tests the html template filter."""
        template_src = u"{% load pages %}{{content|html}}"
        self.assertEqual(self.expanded_html, template.Template(template_src).render(template.Context({"content": self.test_html})))
    
    def testContentTag(self):
        """Tests the content template tag."""
        # Test some templates!
        template_src = u'{%% load pages %%}{%% content "%s" %%}' % self.fieldname
        self.assertEqual(self.expanded_html, template.Template(template_src).render(template.Context({"page": self.subsection})))
        setattr(self.subsection.content, self.fieldname, "")
        self.assertEqual(getattr(self.subsection.content, self.fieldname), "")  # Just make sure that the content area was removed!
        template_src = u'{%% load pages %%}{%% content "%s" inherited %%}' % self.fieldname
        self.assertEqual(self.expanded_html, template.Template(template_src).render(template.Context({"page": self.subsection})))
    
    def testPageUrlTag(self):
        """Tests the page_url template tag."""
        template_src = """{% load pages %}
        {% page_url home %}
        {% page_url home index %}
        {% page_url home as url %}{{url}}
        {% page_url home index as url2 %}{{url2}}
        """
        output_expected = """
        /
        /
        /
        /
        """
        self.assertEqual(output_expected, template.Template(template_src).render(template.Context({"home": self.homepage})))
    
    def testMetaDescriptionTag(self):
        """Tests the meta_description template tag."""
        template_src = "{% load pages %}{% meta_description %}"
        template_obj = template.Template(template_src)
        # Test that page meta description is rendered.
        self.assertEqual(u"", template_obj.render(template.Context({"page": self.subsection})))
        self.section.meta_description = u"foo"
        self.assertEqual(u"foo", template_obj.render(template.Context({"page": self.subsection})))
        self.subsection.meta_description = u"bar"
        self.assertEqual(u"bar", template_obj.render(template.Context({"page": self.subsection})))
        # Test that the meta description can be overridden by a context variable.
        self.assertEqual(u"foobar", template_obj.render(template.Context({"meta_description": "foobar", "page": self.subsection})))
        # Test that the meta description can be set explicitly.
        self.assertEqual(u"foobaz", template.Template("{% load pages %}{% meta_description 'foo' %}{% meta_description baz %}").render(template.Context({"baz": "baz", "page": self.subsection})))
    
    def testMetaKeywordsTag(self):
        """Tests the meta_keywords template tag."""
        template_src = "{% load pages %}{% meta_keywords %}"
        template_obj = template.Template(template_src)
        # Test that page meta keywords is rendered.
        self.assertEqual(u"", template_obj.render(template.Context({"page": self.subsection})))
        self.section.meta_keywords = u"foo"
        self.assertEqual(u"foo", template_obj.render(template.Context({"page": self.subsection})))
        self.subsection.meta_keywords = u"bar"
        self.assertEqual(u"bar", template_obj.render(template.Context({"page": self.subsection})))
        # Test that the meta keywords can be overridden by a context variable.
        self.assertEqual(u"foobar", template_obj.render(template.Context({"meta_keywords": "foobar", "page": self.subsection})))
        # Test that the meta keywords can be set explicitly.
        self.assertEqual(u"foobaz", template.Template("{% load pages %}{% meta_keywords 'foo' %}{% meta_keywords baz %}").render(template.Context({"baz": "baz", "page": self.subsection})))
    
    def testMetaRobotsTag(self):
        """Tests the meta_robots template tag."""
        template_src = "{% load pages %}{% meta_robots %}"
        template_obj = template.Template(template_src)
        # Test that the default is permissive.
        self.assertEqual(u"INDEX, FOLLOW, ARCHIVE", template_obj.render(template.Context({"page": self.subsection})))
        # Test that None can be overridden with False.
        self.homepage.robots_index = False
        self.assertEqual(u"NOINDEX, FOLLOW, ARCHIVE", template_obj.render(template.Context({"page": self.subsection})))
        # Test that False can be overridden with True and None can be overridden with True.
        self.section.robots_index = True
        self.section.robots_follow = True
        self.assertEqual(u"INDEX, FOLLOW, ARCHIVE", template_obj.render(template.Context({"page": self.subsection})))
        # Test that True can be overridden with False.
        self.subsection.robots_index = False
        self.assertEqual(u"NOINDEX, FOLLOW, ARCHIVE", template_obj.render(template.Context({"page": self.subsection})))
        # Test that template variables can override pages.
        self.assertEqual(u"INDEX, FOLLOW, NOARCHIVE", template_obj.render(template.Context({"page": self.subsection, "robots_index": True, "robots_archive": False})))
        # Test that robots can be set explicitly.
        self.assertEqual(u"NOINDEX, FOLLOW, NOARCHIVE", template.Template("{% load pages %}{% meta_robots 0 1 0 %}").render(template.Context({"page": self.subsection})))
    
    def testTitleTag(self):
        """Tests the title template tag."""
        template_src = "{% load pages %}{% title %}"
        template_obj = template.Template(template_src)
        # Test that page titles are rendered.
        self.assertEqual(template.loader.render_to_string("title.html", {"title": "SubSection", "site_title": "Home"}),
                         template_obj.render(template.Context({"page": self.subsection})))
        # Test the browser titles are rendered.
        self.subsection.browser_title = "SubSectionBrowser"
        self.homepage.browser_title = "HomeBrowser"
        self.assertEqual(template.loader.render_to_string("title.html", {"title": "SubSectionBrowser", "site_title": "HomeBrowser"}),
                         template_obj.render(template.Context({"page": self.subsection})))
        # Test that the title can be overidden by a context variable.
        self.assertEqual(template.loader.render_to_string("title.html", {"title": "Foo", "site_title": "HomeBrowser"}),
                         template_obj.render(template.Context({"page": self.subsection,
                                                               "title": "Foo"})))
        # Test that the title can be explicitly given.
        self.assertEqual(template.loader.render_to_string("title.html", {"title": "Bar", "site_title": "HomeBrowser"}),
                         template.Template("{% load pages %}{% title 'Bar' %}").render(template.Context({"page": self.subsection})))
    
    def assertContainsPageLink(self, html, page, is_here, short_title_override=None):
        """Tests that the given html contains a link to the given page."""
        links = re.findall(ur"<a(.+?)>(.+?)</a>", html, re.IGNORECASE)
        for attrs, short_title in links:
            attr_dict = dict(re.findall(ur"\s(\w+)=[\"'](.*?)[\"']", attrs, re.IGNORECASE))
            if attr_dict["href"] == page.get_absolute_url():
                self.assertEqual(short_title, short_title_override or page.short_title)
                self.assertEqual(attr_dict["title"], page.title)
                if is_here:
                    self.assertTrue("here" in attr_dict.get("class", ""))
                else:
                    self.assertFalse("here" in attr_dict.get("class", ""))
                return
        self.assertTrue(False, "No page link for page '%s' found" % page)
    
    def testNavPrimaryTag(self):
        """Tests the nav_primary template tag."""
        template_src = u"{% load pages %}{% nav_primary %}"
        template_obj = template.Template(template_src)
        self.homepage.short_title = "HomeShort"
        self.homepage.save()
        self.section.short_title = "SectionShort"
        self.section.save()
        # Test that the homepage is highlighted.
        nav_primary_html = template_obj.render(template.Context({"page": self.homepage}))
        self.assertContainsPageLink(nav_primary_html, self.homepage, True, "Home")
        self.assertContainsPageLink(nav_primary_html, self.section, False)
        # Test that sections are highlighted.
        nav_primary_html = template_obj.render(template.Context({"page": self.subsection}))
        self.assertContainsPageLink(nav_primary_html, self.homepage, False, "Home")
        self.assertContainsPageLink(nav_primary_html, self.section, True)
    
    def testNavSecondaryTag(self):
        """Tests the nav_secondary template tag."""
        template_src = u"{% load pages %}{% nav_secondary %}"
        template_obj = template.Template(template_src)
        self.section.short_title = "SectionShort"
        self.section.save()
        self.subsection.short_title = "SubSectionShort"
        self.subsection.save()
        # Test that the section is highlighted.
        nav_secondary_html = template_obj.render(template.Context({"page": self.section}))
        self.assertContainsPageLink(nav_secondary_html, self.section, True)
        self.assertContainsPageLink(nav_secondary_html, self.subsection, False)
        # Test that subsections are highlighted.
        nav_secondary_html = template_obj.render(template.Context({"page": self.subsection}))
        self.assertContainsPageLink(nav_secondary_html, self.section, False)
        self.assertContainsPageLink(nav_secondary_html, self.subsection, True)
        
    def testNavTertiaryTag(self):
        """Tests the nav_tertiary template tag."""
        template_src = u"{% load pages %}{% nav_tertiary %}"
        template_obj = template.Template(template_src)
        self.subsection.short_title = "SubSectionShort"
        self.subsection.save()
        self.subsubsection.short_title = "SubSubSectionShort"
        self.subsubsection.save()
        # Test that the subsection is highlighted.
        nav_tertiary_html = template_obj.render(template.Context({"page": self.subsection}))
        self.assertContainsPageLink(nav_tertiary_html, self.subsection, True)
        self.assertContainsPageLink(nav_tertiary_html, self.subsubsection, False)
        # Test that subsubsections are highlighted.
        nav_tertiary_html = template_obj.render(template.Context({"page": self.subsubsection}))
        self.assertContainsPageLink(nav_tertiary_html, self.subsection, False)
        self.assertContainsPageLink(nav_tertiary_html, self.subsubsection, True)
    
    def testBreadcrumbsTag(self):
        """Tests the breadcrumbs template tag."""
        self.homepage.short_title = "HomeShort"
        self.homepage.save()
        self.section.short_title = "SectionShort"
        self.section.save()
        self.subsection.short_title = "SubSectionShort"
        self.subsection.save()
        # Test that the unextended breadcrumbs are rendered.
        breadcrumbs_html = template.Template(u"{% load pages %}{% breadcrumbs %}").render(template.Context({"page": self.subsection}))
        self.assertContainsPageLink(breadcrumbs_html, self.homepage, False)
        self.assertContainsPageLink(breadcrumbs_html, self.section, False)
        # Test that the extended breadcrumbs are rendered.
        breadcrumbs_html = template.Template(u"{% load pages %}{% breadcrumbs extended %}").render(template.Context({"page": self.subsection}))
        self.assertContainsPageLink(breadcrumbs_html, self.homepage, False)
        self.assertContainsPageLink(breadcrumbs_html, self.section, False)
        self.assertContainsPageLink(breadcrumbs_html, self.subsection, False)
    
    def testHeaderTag(self):
        """Tests the header template tag."""
        template_src = u"{% load pages %}{% header %}"
        template_obj = template.Template(template_src)
        # Test that the page header is rendered.
        self.assertEqual(u"Section", template_obj.render(template.Context({"page": self.section})))
        # Test that a context variable can override the page header.
        self.assertEqual(u"Foo", template_obj.render(template.Context({"page": self.section, "title": "Foo"})))
        self.assertEqual(u"Bar", template_obj.render(template.Context({"page": self.section, "title": "Foo", "header": "Bar"})))
        # Test that the title can be explicitly given.
        self.assertEqual(u"Baz", template.Template("{% load pages %}{% header 'Baz' %}").render(template.Context({"page": self.section})))
    
    def tearDown(self):
        """Destroys the test case."""
        self.file.delete()
        default_storage.delete(TEMP_FILE_NAME)
        self.homepage.delete()
        
        