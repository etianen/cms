"""Models used by the version control application."""


from django.contrib.admin.models import LogEntry
from django.db import models


class Version(models.Model):
    
    """An entry of version data."""
    
    log_entry = models.OneToOneField(LogEntry,
                                     primary_key=True)
    
    data = models.TextField()
    
    