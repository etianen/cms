"""Upgrades the application data version 2.0.1 to 2.1."""


from django.core.management.base import NoArgsCommand
from django.core.management import call_command
from django.db import transaction, models, connection

from cms.apps.media.models import File


class Command(NoArgsCommand):
    
    help = "Upgrades the CMS data from version 2.0.1 to 2.1."
    
    @transaction.commit_on_success
    def handle_noargs(self, **options):
        """Upgrades the application from version 2.0.1 to 2.1."""
        print "Upgrading CMS data from 2.0.1 to 2.1"
        cursor = connection.cursor()
        # Get the old image content type id.
        cursor.execute("SELECT id FROM django_content_type WHERE app_label='media' AND model='image';")
        image_content_type_id, = cursor.fetchone()
        # Get all old image data.
        cursor.execute("SELECT id, title, last_modified, folder_id, file FROM media_image;")
        images = cursor.fetchall()
        # Delete old file fields.
        cursor.execute("ALTER TABLE media_file DROP COLUMN size;")
        cursor.execute("ALTER TABLE media_file DROP COLUMN keywords;")
        cursor.execute("ALTER TABLE media_file DROP COLUMN notes;")
        transaction.set_dirty()
        # Create new files.
        files = []
        for image_id, image_title, image_last_modified, folder_id, file in images:
            files.append(File.objects.create(title=image_title, last_modified=image_last_modified, folder_id=folder_id, file=file))
        # Update all model content areas.
        
        # Update all 
        
        # Synchronize the content types.
        call_command("syncdb")
        
        