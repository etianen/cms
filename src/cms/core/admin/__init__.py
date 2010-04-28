"""Core CMS admin functionality."""


from cms.core.admin.sites import AdminSite
from cms.core.admin.base import PageBaseAdmin, PublishedModelAdmin, get_date_modified  # @UnusedImport


site= AdminSite()