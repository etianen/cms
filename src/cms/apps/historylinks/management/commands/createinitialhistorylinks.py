from django.core.management.base import NoArgsCommand
from django.db import transaction

from cms.core.models.managers import publication_manager
from cms.apps.historylinks.registration import get_registered_models
from cms.apps.historylinks.models import HistoryLink


class Command(NoArgsCommand):

    help = "Creates the initial history links for all registered models."

    @transaction.commit_on_success
    def handle_noargs(self, **options):
        with publication_manager.select_published(False):
            link_count = 0
            # Create links.
            for model in get_registered_models():
                for obj in model._default_manager.all().iterator():
                    created, _ = HistoryLink.objects.create_for_obj(obj)
                    if created:
                        link_count += 1
            self.stdout.write("Successfully created initial history links for {link_count} object(s).\n".format(
                link_count = link_count,
            ))