"""Syncronizes the site with the current settings file."""


from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):

    help = "Syncronizes the current site with the value from the Django settings file."
    
    def handle_noargs(self, **options):
        """Runs the command."""
        site = Site.objects.get_current()
        site.name = settings.SITE_NAME
        domain = settings.SITE_DOMAIN
        if settings.PREPEND_WWW and not domain.startswith("www."):
            domain = "www." + domain
        site.domain = domain
        site.save()
        
        