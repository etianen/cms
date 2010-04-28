"""Upgrades the application data version 2.0.1 to 2.1."""


from __future__ import with_statement

from xml.dom import minidom

from django.core.management.base import NoArgsCommand
from django.core.management import call_command
from django.core.serializers.xml_serializer import getInnerText
from django.db import transaction

from cms.apps.pages.models import Page
from cms.apps.pages.models.managers import publication_manager


class Command(NoArgsCommand):
    
    help = "Upgrades the CMS data from version 2.0.1 to 2.1."
    
    @transaction.commit_on_success
    def handle_noargs(self, **options):
        """Upgrades the application from version 2.0.1 to 2.1."""
        with publication_manager.select_published(False):
            print "Upgrading CMS data from 2.1 to 2.2"
            # Rename all redirects content to links.
            for page in Page.objects.filter(content_type="redirect"):
                page.content_type = "link"
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
            # Synchronize the content types.
            call_command("syncdb")
            print "Upgrade complete!"
        
        