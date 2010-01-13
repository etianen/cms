"""Upgrades the application data version 2.0.1 to 2.1."""


from __future__ import with_statement

from django.core.management.base import NoArgsCommand
from django.core.management import call_command
from django.core import urlresolvers
from django.db import transaction, models, connection

from cms.apps.pages import content, permalinks
from cms.apps.pages.models import HtmlField, Page
from cms.apps.pages.models.managers import publication_manager
from cms.apps.media.models import File


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
            # Create a function to update HTML content.
            image_permalinks = [(urlresolvers.reverse("permalink_redirect", kwargs={"content_type_id": image_content_type_id, "object_id": image_id}), image_id)
                                for image_id, image_title, image_last_modified, folder_id, file in images]
            def replace_image_permalinks(obj, field_name):
                html = getattr(obj, field_name)
                for old_permalink, image_id in image_permalinks:
                    new_permalink = unicode(permalinks.create(files[image_id]))
                    html = html.replace(unicode(old_permalink), new_permalink)
                setattr(obj, field_name, html)
            # Update all model HTML fields.
            for model in models.get_models():
                html_fields = []
                for field in model._meta.fields:
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
                        replace_image_permalinks(page_content, html_field.name)
                    page.content = page_content
                    page.save()
            # Synchronize the content types.
            call_command("syncdb")
            print "Upgrade complete!"
        
        