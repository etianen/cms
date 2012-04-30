"""Optional external libraries that enhance the CMS."""

from django.conf import settings


# Reversion shim.

has_reversion = "reversion" in settings.INSTALLED_APPS

if has_reversion:
    from reversion.admin import VersionMetaAdminMixin
else:
    VersionMetaAdminMixin = object