from django.core.management.base import NoArgsCommand
from django.db import transaction

from cms.core.models.managers import publication_manager
from cms.apps.permalinks.registration import get_registered_models
from cms.apps.permalinks.models import Permalink


class Command(NoArgsCommand):

    help = "Creates the initial permalinks for all registered models."

    @transaction.commit_on_success
    def handle_noargs(self, **options):
        with publication_manager.select_published(False):
            permalink_count = 0
            # Create permalinks.
            for model in get_registered_models():
                for obj in model._default_manager.all().iterator():
                    created, _ = Permalink.objects.create_for_obj(obj)
                    if created:
                        permalink_count += 1
            self.stdout.write("Successfully created initial permalinks for {permalink_count} object(s).\n".format(
                permalink_count = permalink_count,
            ))