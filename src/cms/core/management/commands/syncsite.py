from django.core.management.base import NoArgsCommand
from django.conf import settings
from django.contrib.sites.models import Site
from django.db import transaction


class Command(NoArgsCommand):

    help = "Syncronizes the site name and domain in the Django settings with the Site model in the database."

    @transaction.commit_on_success
    def handle_noargs(self, **options):
        site = Site.objects.get_current()
        site.name = settings.SITE_NAME
        domain = settings.SITE_DOMAIN
        if settings.PREPEND_WWW and not domain.startswith("www."):
            domain = "www." + domain
        site.domain = domain
        site.save()
        self.stdout.write("Successfully set current site to {0} ({1}).\n".format(site.domain, site.name))