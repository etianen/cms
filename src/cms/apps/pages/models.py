"""Core models used by the CMS."""


import datetime

from django import forms, template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.base import ModelBase
from django.http import Http404
from django.shortcuts import render_to_response

from cms.apps.pages import content
from cms.apps.pages.optimizations import cached_getter, cached_setter
from cms.apps.pages.serializers import serializer


PAGE_PUBLICATION_SELECT_SQL = """
    is_online = TRUE AND
    (
        (
            publication_date IS NULL OR
            publication_date <= CURRENT_DATE()
        ) AND
        (
            expiry_date IS NULL OR
            expiry_date > CURRENT_DATE()
        )
    )
"""


PAGE_PUBLICATION_WHERE_SQL = "is_published = TRUE"


class PageBaseManager(models.Manager):
    
    """
    Base manager for all pages.
    
    This must be subclassed when creating managers for Page subclasses.
    """
    
    def get_query_set(self):
        """Adds the is_published property to all loaded pages."""
        queryset = super(PageBaseManager, self).get_query_set()
        queryset = queryset.extra(select={"is_published": PAGE_PUBLICATION_SELECT_SQL})
        return queryset


class PublishedManagerProxy(object):
    
    """Manager that only returns published content."""
    
    def __get__(self, instance, cls):
        """Returns a filtered queryset which only contains published objects."""
        if instance != None:
            raise AttributeError, "Manager isn't accessible via %s instances" % type.__name__
        # Filter the queryset.
        return cls.objects.extra(where=[PAGE_PUBLICATION_WHERE_SQL])


class ContentRegistrationError(Exception):
    
    """Exception raised when content registration goes wrong."""


class SimpleContent(content.Content):
    
    """The default page content associated by default with all pages."""
    
    verbose_name = "content"
    
    verbose_name_plural = "content"
    
    content = content.HtmlField()


class PageMetaClass(ModelBase):
    
    """Metaclass for Page models."""
    
    def __init__(self, name, bases, attrs):
        """Initializes the PageMetaClass."""
        super(PageMetaClass, self).__init__(name, bases, attrs)
        self.content_registry = {}
        self.register_content(SimpleContent, "content")

    def register_content(self, content_cls, slug=None):
        """
        Registers the given content type with this class under the given slug.
        """
        slug = slug or content_cls.__name__.lower()
        self.content_registry[slug] = content_cls
      
    def unregister_content(self, slug):
        """Unregisters the content type associated with the given slug."""
        try:
            del self.content_registry[slug]
        except KeyError:
            raise ContentRegistrationError, "No content type is registered under %r." % slug
    
    def lookup_content(self, slug):
        """Looks up the given content type by type slug."""
        try:
            return self.content_registry[slug]
        except KeyError:
            raise ContentRegistrationError, "No content type is registered under %r." % slug
  
  
class PageBase(models.Model):
    
    """Base model for models used to generate a HTML page."""
    
    __metaclass__ = PageMetaClass
    
    # Model managers.
    
    objects = PageBaseManager()
    
    published_objects = PublishedManagerProxy()
        
    # Base fields.
    
    title = models.CharField(max_length=1000)
    
    url_title = models.SlugField("URL title")
    
    last_modified = models.DateTimeField(auto_now=True,
                                         help_text="The date and time of when this content was last modified.")
    
    # Publication fields.
    
    is_online = models.BooleanField("online",
                                    default=True)
    
    publication_date = models.DateTimeField(blank=True,
                                            null=True,
                                            help_text="The date that this page will appear on the website.  Leave this blank to immediately publish this page.")

    expiry_date = models.DateTimeField(blank=True,
                                       null=True,
                                       help_text="The date that this page will be removed from the website.  Leave this blank to never expire this page.")
    
    # Navigation fields.
    
    short_title = models.CharField(max_length=100,
                                   blank=True,
                                   null=True,
                                   help_text="A shorter version of the title that will be used in site navigation. Leave blank to use the full-length title.")
    
    # SEO fields.
    
    browser_title = models.CharField(max_length=1024,
                                     blank=True,
                                     null=True,
                                     help_text="The heading to use in the user's web browser.  Leave blank to use the page title.  Search engines page particular attention to this attribute.")
    
    keywords = models.CharField(max_length=1024,
                                blank=True,
                                null=True,
                                help_text="A comma-separated list of keywords for this page. Use this to specify common mis-spellings or alternative versions of important words in this page.")

    description = models.TextField(blank=True,
                                   null=True,
                                   help_text="A brief description of the contents of this page. Leave blank to use to use the parent page description.")
    
    priority = models.FloatField(choices=settings.SEO_PRIORITIES,
                                 default=settings.SEO_DEFAULT_PRIORITY,
                                 blank=True,
                                 null=True,
                                 help_text="The relative importance of this content in your site.  Search engines use this as a hint when ranking the pages within your site.")
    
    change_frequency = models.CharField(max_length=255,
                                        choices=settings.SEO_CHANGE_FREQUENCIES,
                                        default=settings.SEO_DEFAULT_CHANGE_FREQUENCY,
                                        blank=True,
                                        null=True,
                                        help_text="How frequently you expect this content to be updated.  Search engines use this as a hint when scanning your site for updates.")
    
    allow_indexing = models.BooleanField(default=True,
                                         help_text="Uncheck this box to prevent search engines from indexing this page. Disable this only if the page contains information which you do not wish to show up in search results.")

    allow_archiving = models.BooleanField(default=True,
                                          help_text="Uncheck this box to prevent search engines from archiving this page. Disable this only if the page is likely to change on a very regular basis.")

    follow_links = models.BooleanField(default=True,
                                       help_text="Uncheck this box to prevent search engines from following any links they find in this page. Disable this only if the page contains links to other sites that you do not wish to publicise.")
    
    # Content fields.

    content_type = models.CharField(max_length=20,
                                    editable=False,
                                    help_text="The type of page content.")

    content_data = models.TextField(editable=False,
                                    help_text="The encoded data of this page.")

    @cached_getter
    def get_content(self):
        """Returns the content object associated with this page."""
        if not self.content_type:
            return None
        content_cls = self.__class__.lookup_content(self.content_type)
        if self.content_data:
            content_data = serializer.deserialize(self.content_data)
        else:
            content_data = {}
        content_instance = content_cls(self, content_data)
        return content_instance

    @cached_setter(get_content)
    def set_content(self, content):
        """Sets the content object for this page."""
        self.content_data = serializer.serialize(content.data)

    content = property(get_content,
                       set_content,
                       doc="The content object associated with this page.")
    
    # Page rendering methods.
    
    def render_to_response(self, request, extra_context=None, template_name=None, **kwargs):
        """
        Dispatches the request to this page.
        
        Returns a HttpResponse of some sort.
        """
        # Check for publication state.
        if not self.is_published:
            if not (request.user.is_authenticated() and request.user.is_staff and request.user.is_active):
                raise Http404, "The page '%s' has not been published yet." % self
        # Render the template.
        if template_name is None:
            template_name = "%s/%s.html" % (self._meta.app_label, self.__class__.__name__.lower())
        context = {}
        context.update(extra_context or {})
        return render_to_response(template_name, context, template.RequestContext(request), **kwargs)
    
    # Base model methods.
    
    def __unicode__(self):
        """
        Returns the short title of this page, falling back to the standard
        title.
        """
        return self.short_title or self.title
    
    class Meta:
        abstract = True
        ordering = ("title",)


class PageManager(PageBaseManager):
    
    """Manager for Page objects."""
    
    def get_homepage(self):
        """Returns the site homepage."""
        return self.get(parent=None)


class Page(PageBase):

    """A page within the site."""

    objects = PageManager()
    
    # Hierarchy fields.

    parent = models.ForeignKey("self",
                               blank=True,
                               null=True)

    order = models.PositiveSmallIntegerField(unique=True,
                                             editable=False,
                                             blank=True,
                                             null=True)

    def get_all_parents(self):
        """Returns a list of all parents of this page."""
        if self.parent:
            return [self.parent] + self.parent.all_parents
        return []
    
    all_parents = property(get_all_parents,
                           doc="A list of all parents of this page.")

    def get_breadcrumbs(self):
        """Returns the breadcrumb trail for this page."""
        return reversed([self] + self.all_parents)

    breadcrumbs = property(get_breadcrumbs,
                           doc="The breadcrumb trail for this page.")

    @cached_getter
    def get_children(self):
        """
        Returns all the children of this page, regardless of their publication
        state.
        """
        return Page.objects.filter(parent=self).order_by("order", "id")

    children = property(get_children,
                        doc="All the children of this page, regardless of their publication state.")

    def get_all_children(self):
        """
        Returns all the children of this page, cascading down to their children
        too.
        """
        children = []
        for child in self.children:
            children.append(child)
            children.extend(child.all_children)
        return children
            
    all_children = property(get_all_children,
                            doc="All the children of this page, cascading down to their children too.")

    @cached_getter
    def get_published_children(self):
        """Returns all the published children of this page."""
        return Page.published_objects.filter(parent=self).order_by("order", "id")

    published_children = property(get_published_children,
                                  doc="All the published children of this page.")

    # Navigation fields.

    in_navigation = models.BooleanField("add to navigation",
                                        default=True,
                                        help_text="Uncheck this box to remove this content from the site navigation.")

    @cached_getter
    def get_navigation(self):
        """
        Returns all published children of this page in the site navigation.
        """
        return self.content.get_navigation()

    navigation = property(get_navigation,
                          doc="All the published children of this page in the site navigation.")

    # Standard model methods.
    
    def get_absolute_url(self):
        """Generates the absolute url of the page."""
        if self.parent:
            return self.parent.get_absolute_url() + self.url_title + "/"
        return reverse("render_homepage")

    class Meta:
        unique_together = (("parent", "url_title",),)


# Add some base content types.


class Redirect(content.Content):
    
    """A redirect to another URL."""
    
    icon = settings.CMS_MEDIA_URL + "img/content-types/redirect.png"
    
    redirect_url = content.CharField(help_text="The URL where the user will be redirected.")
    
       
Page.register_content(Redirect)
