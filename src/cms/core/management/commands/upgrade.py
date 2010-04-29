"""Upgrades the application data version 2.0.1 to 2.1."""


from __future__ import with_statement

from xml.dom import minidom

from django.core.management.base import NoArgsCommand
from django.core.management import call_command
from django.core.serializers.xml_serializer import getInnerText
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import transaction, connection

from cms.core.models.managers import publication_manager
from cms.apps.pages.content import registered_content, get_add_permission
from cms.apps.pages.models import Page


class Command(NoArgsCommand):
    
    help = "Upgrades the CMS data from version 2.0.1 to 2.1."
    
    @transaction.commit_on_success
    def handle_noargs(self, **options):
        """Upgrades the application from version 2.0.1 to 2.1."""
        with publication_manager.select_published(False):
            print "Upgrading CMS data from 2.1 to 2.2"
            # Migrate the database.
            connection.cursor().execute("ALTER TABLE pages_page ADD COLUMN date_created DATETIME NOT NULL")
            connection.cursor().execute("UPDATE pages_page SET date_created = NOW()")
            connection.cursor().execute("ALTER TABLE pages_page CHANGE COLUMN last_modified date_modified DATETIME NOT NULL")
            connection.cursor().execute("ALTER TABLE pages_page DROP INDEX `order`")
            connection.cursor().execute("ALTER TABLE pages_page MODIFY COLUMN `order` INTEGER UNSIGNED")
            
            connection.cursor().execute("ALTER TABLE news_article ADD COLUMN date_created DATETIME NOT NULL")
            connection.cursor().execute("UPDATE news_article SET date_created = NOW()")
            connection.cursor().execute("ALTER TABLE news_article CHANGE COLUMN last_modified date_modified DATETIME NOT NULL")
            
            connection.cursor().execute("ALTER TABLE events_event ADD COLUMN date_created DATETIME NOT NULL")
            connection.cursor().execute("UPDATE events_event SET date_created = NOW()")
            connection.cursor().execute("ALTER TABLE events_event CHANGE COLUMN last_modified date_modified DATETIME NOT NULL")
            
            connection.cursor().execute("ALTER TABLE media_file ADD COLUMN date_created DATETIME NOT NULL")
            connection.cursor().execute("UPDATE media_file SET date_created = NOW()")
            connection.cursor().execute("ALTER TABLE media_file CHANGE COLUMN last_modified date_modified DATETIME NOT NULL")
            
            connection.cursor().execute("ALTER TABLE media_folder ADD COLUMN date_created DATETIME NOT NULL")
            connection.cursor().execute("UPDATE media_folder SET date_created = NOW()")
            connection.cursor().execute("ALTER TABLE media_folder ADD COLUMN date_modified DATETIME NOT NULL")
            connection.cursor().execute("UPDATE media_folder SET date_modified = NOW()")
            # Rename all redirects content to links.
            for page in Page.objects.filter(content_type="redirect"):
                page.content_type = "links.Link"
                raw_data = {}
                xml_data = minidom.parseString(page.content_data.encode("utf8")).documentElement
                for element in xml_data.getElementsByTagName("attribute"):
                    key = element.attributes["name"].nodeValue
                    value = getInnerText(element)
                raw_data[key] = value
                content = page.content
                content.link_url = raw_data["redirect_url"]
                page.content = content
                page.save()
            # Add the app_label to content registration keys.
            for page in Page.objects.all():
                for content_type in registered_content.values():
                    if content_type.__name__.lower() == page.content_type:
                        page.content_type = content_type.registration_key
                page.save()
            # Migrate old permissions to new.
            for content_type in registered_content.values():
                old_slug = content_type.__name__.lower()
                try:
                    permission_name = get_add_permission(old_slug)
                except ValueError:
                    continue
                try:
                    perm = Permission.objects.get(codename=permission_name, content_type=ContentType.objects.get_for_model(Page))
                except Permission.DoesNotExist:
                    continue
                new_perm_name = get_add_permission(content_type.registration_key)
                perm.codename = new_perm_name
                perm.save()
            # Synchronize the content types.
            call_command("syncdb")
            print "Upgrade complete!"
        
        