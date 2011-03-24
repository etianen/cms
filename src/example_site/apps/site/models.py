"""Custom content classes."""

from django.db import models

from cms.core.models import HtmlField
from cms.apps.pages.models import ContentBase


class Content(ContentBase):
    
    content_primary = HtmlField(
        "primary content",
        blank = True
    )