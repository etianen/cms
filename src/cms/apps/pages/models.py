"""Core models used by the CMS."""

from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.db import models, connection
from django.db.models import Q, F
from django.utils.functional import cached_property
from django.utils import timezone

from cms import sitemaps, externals
from cms.models import PageBase, OnlineBaseManager, PageBaseSearchAdapter
from cms.models.managers import publication_manager


def get_default_page_parent():
    """Returns the default page parent."""
    try:
        return Page.objects.all()[0]
    except IndexError:
        return None


class PageManager(OnlineBaseManager):
    
    """Manager for Page objects."""
    
    def select_published(self, queryset, page_alias=None):
        """Selects only published pages."""
        queryset = super(PageManager, self).select_published(queryset)
        now = timezone.now()
        # Perform local filtering.
        queryset = queryset.filter(Q(publication_date=None) | Q(publication_date__lte=now))
        queryset = queryset.filter(Q(expiry_date=None) | Q(expiry_date__gt=now))
        # Perform parent ordering.
        quote_name = connection.ops.quote_name
        page_alias = page_alias  or quote_name("pages_page")
        queryset = queryset.extra(
            where = ("""
                NOT EXISTS (
                    SELECT *
                    FROM {pages_page} AS {ancestors}
                    WHERE
                        {ancestors}.{left} < {page_alias}.{left} AND
                        {ancestors}.{right} > {page_alias}.{right} AND (
                            {ancestors}.{is_online} = FALSE OR
                            {ancestors}.{publication_date} > %s OR
                            {ancestors}.{expiry_date} <= %s
                        )
                )
            """.format(
                page_alias = page_alias,
                **dict(
                    (name, quote_name(name))
                    for name in (
                        "pages_page",
                        "ancestors",
                        "left",
                        "right",
                        "is_online",
                        "publication_date",
                        "expiry_date",
                    )
                )
            ),),
            params = (now, now),
        )
        return queryset
    
    def get_homepage(self):
        """Returns the site homepage."""
        return self.prefetch_related("child_set__child_set").get(parent=None)


class Page(PageBase):

    """A page within the site."""
    
    objects = PageManager()
    
    # Hierarchy fields.

    parent = models.ForeignKey(
        "self",
        blank = True,
        null = True,
        default = get_default_page_parent,
        related_name = "child_set",
    )

    left = models.IntegerField(
        editable = False,
        db_index = True,
    )
    
    right = models.IntegerField(
        editable = False,
        db_index = True,
    )
    
    @cached_property
    def children(self):
        """The child pages for this page."""
        children = []
        if self.right - self.left > 1:  # Optimization - don't fetch children we know aren't there!
            for child in self.child_set.all():
                child.parent = self
                children.append(child)
        return children
    
    @property
    def navigation(self):
        """The sub-navigation of this page."""
        return [child for child in self.children if child.in_navigation]
    
    # Publication fields.
    
    publication_date = models.DateTimeField(
        blank = True,
        null = True,
        db_index = True,
        help_text = "The date that this page will appear on the website.  Leave this blank to immediately publish this page.",
    )

    expiry_date = models.DateTimeField(
        blank = True,
        null = True,
        db_index = True,
        help_text = "The date that this page will be removed from the website.  Leave this blank to never expire this page.",
    )

    # Navigation fields.

    in_navigation = models.BooleanField(
        "add to navigation",
        default = True,
        help_text = "Uncheck this box to remove this content from the site navigation.",
    )

    # Content fields.
    
    content_type = models.ForeignKey(
        ContentType,
        editable = False,
        help_text="The type of page content.",
    )
    
    @cached_property
    def content(self):
        """The associated content model for this page."""
        content_cls = ContentType.objects.get_for_id(self.content_type_id).model_class()
        content = content_cls._default_manager.get(page=self)
        content.page = self
        return content

    def reverse(self, view_func, args=None, kwargs=None):
        """Performs a reverse URL lookup."""
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}
        urlconf = ContentType.objects.get_for_id(self.content_type_id).model_class().urlconf
        return self.get_absolute_url() + urlresolvers.reverse(view_func, args=args, kwargs=kwargs, urlconf=urlconf, prefix="")

    # Standard model methods.
    
    def get_absolute_url(self):
        """Generates the absolute url of the page."""
        if self.parent:
            return self.parent.get_absolute_url() + self.url_title + "/"
        return urlresolvers.get_script_prefix()
    
    # Tree management.
    
    @property
    def _branch_width(self):
        return self.right - self.left + 1
    
    def _excise_branch(self):
        """Excises this whole branch from the tree."""
        branch_width = self._branch_width
        Page.objects.filter(left__gte=self.left).update(
            left = F("left") - branch_width,
        )
        Page.objects.filter(right__gte=self.left).update(
            right = F("right") - branch_width,
        )
        
    def _insert_branch(self):
        """Inserts this whole branch into the tree."""
        branch_width = self._branch_width
        Page.objects.filter(left__gte=self.left).update(
            left = F("left") + branch_width,
        )
        Page.objects.filter(right__gte=self.left).update(
            right = F("right") + branch_width,
        )
        
    def save(self, *args, **kwargs):
        """Saves the page."""
        # Lock entire table.
        existing_pages = dict(
            (page["id"], page)
            for page
            in Page.objects.all().select_for_update().values("id", "parent_id", "left", "right")
        )
        if self.left is None or self.right is None:
            # This page is being inserted.
            if existing_pages:
                parent_right = existing_pages[self.parent_id]["right"]
                # Set the model left and right.
                self.left = parent_right
                self.right = self.left + 1
                # Update the whole tree structure.
                self._insert_branch()
            else:
                # This is the first page to be created, ever!
                self.left = 1
                self.right = 2
        else:
            # This is an update.
            old_parent_id = existing_pages[self.id]["parent_id"]
            if old_parent_id != self.parent_id:
                # The page has moved.
                branch_width = self.right - self.left + 1
                # Disconnect child branch.
                if branch_width > 2:
                    Page.objects.filter(left__gt=self.left, right__lt=self.right).update(
                        left = F("left") * -1,
                        right = F("right") * -1,
                    )
                self._excise_branch()
                # Store old left and right values.
                old_left = self.left
                old_right = self.right
                # Put self into the tree.
                parent_right = existing_pages[self.parent_id]["right"]
                if parent_right > self.right:
                    parent_right -= self._branch_width
                self.left = parent_right
                self.right = self.left + branch_width - 1
                self._insert_branch()
                # Put all children back into the tree.
                if branch_width > 2:
                    child_offset = self.left - old_left
                    Page.objects.filter(left__lt=-old_left, right__gt=-old_right).update(
                        left = (F("left") - child_offset) * -1,
                        right = (F("right") - child_offset) * -1,
                    )
        # Now actually save it!
        super(Page, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Deletes the page."""
        list(Page.objects.all().select_for_update().values_list("left", "right"))  # Lock entire table.
        super(Page, self).delete(*args, **kwargs)
        # Update the entire tree.
        self._excise_branch()

    class Meta:
        unique_together = (("parent", "url_title",),)
        ordering = ("left",)


externals.historylinks("register", Page)


class PageSitemap(sitemaps.PageBaseSitemap):
    
    """Sitemap for page models."""
    
    model = Page
    
    def items(self):
        """Only lists items that are marked as indexable."""
        return filter_indexable_pages(super(PageSitemap, self).items())


sitemaps.register(Page, sitemap_cls=PageSitemap)


class PageSearchAdapter(PageBaseSearchAdapter):
    
    """Search adapter for Page models."""
    
    def get_content(self, obj):
        """Returns the search text for the page."""
        content_obj = obj.content
        return u" ".join((
            super(PageSearchAdapter, self).get_content(obj),
            self.prepare_content(u" ".join(
                unicode(self._resolve_field(content_obj, field_name))
                for field_name in (
                    field.name for field
                    in content_obj._meta.fields
                    if isinstance(field, (models.CharField, models.TextField))
                )
            ))
        ))
        
    def get_live_queryset(self):
        """Selects the live page queryset."""
        # HACK: Prevents a table name collision in the Django queryset manager.
        with publication_manager.select_published(False):
            qs = Page._base_manager.all()
        if publication_manager.select_published_active():
            qs = Page.objects.select_published(qs, page_alias="U0")
        # Filter out unindexable pages.
        qs = filter_indexable_pages(qs)
        # All done!
        return qs
        
        
externals.watson("register", Page, adapter_cls=PageSearchAdapter)


# Base content class.

def get_registered_content():
    """Returns a list of all registered content objects."""
    return [
        model for model in models.get_models()
        if issubclass(model, ContentBase) and not model._meta.abstract
    ]
    
    
def filter_indexable_pages(queryset):
    """
    Filters the given queryset of pages to only contain ones that should be
    indexed by search engines.
    """
    return queryset.filter(
        robots_index = True,
        content_type__in = [
            ContentType.objects.get_for_model(content_model)
            for content_model
            in get_registered_content()
            if content_model.robots_index
        ]
    )
    

class ContentBase(models.Model):
    
    """Base class for page content."""
    
    # This must be a 64 x 64 pixel image.
    icon = "pages/img/content.png"

    # The heading that the admin places this content under.
    classifier = "content"

    # The urlconf used to power this content's views.
    urlconf = "cms.apps.pages.urls"
    
    # A fieldset definition. If blank, one will be generated.
    fieldsets = None
    
    # Whether pages of this type should be included in search indexes. (Can still be disabled on a per-page basis).
    robots_index = True
    
    page = models.OneToOneField(
        Page,
        primary_key = True,
        editable = False,
        related_name = "+",
    )
    
    def __unicode__(self):
        """Returns a unicode representation."""
        return unicode(self.page)
    
    class Meta:
        abstract = True