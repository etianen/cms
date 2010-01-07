"""Upgrades the application data version 2.0.1 to 2.1."""


from __future__ import with_statement

from django.core.management.base import NoArgsCommand
from django.core.management import call_command
from django.db import transaction, models, connection

from cms.apps.pages import content
from cms.apps.pages.models import HtmlField, Page
from cms.apps.pages.models.managers import publication_manager
from cms.apps.media.models import File


def replace_image_permalinks(obj, field_name):
    """Replaces all image permalinks in the given field."""
    html = getattr(obj, field_name)
    
    
    setattr(obj, field_name, html)


class Command(NoArgsCommand):
    
    help = "Upgrades the CMS data from version 2.0.1 to 2.1."
    
    @transaction.commit_on_success
    def handle_noargs(self, **options):
        """Upgrades the application from version 2.0.1 to 2.1."""
        with publication_manager.select_published(False):
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
            files = {}
            for image_id, image_title, image_last_modified, folder_id, file in images:
                files[image_id] = File.objects.create(title=image_title, last_modified=image_last_modified, folder_id=folder_id, file=file)
            # Update all model HTML fields.
            for model in models.get_models():
                html_fields = []
                for field in model._meta.get_fields():
                    if isinstance(field, HtmlField):
                        html_fields.append(field)
                if html_fields:
                    for obj in model._default_manager.iterator():
                        for html_field in html_fields:
                            replace_image_permalinks(obj, html_field.attname)
                        obj.save()
            # Update all page content HTML fields.
            for page in Page.objects.iterator():
                page_content = page.content
                html_fields = []
                for field in page_content.fields:
                    if isinstance(field, content.HtmlField):
                        html_fields.append(field)
                if html_fields:
                    for html_field in html_fields:
                        replace_image_permalinks(obj, html_field.name)
                    page.save()
            # Synchronize the content types.
            call_command("syncdb")
        
        