"""Admin classes used by the version control applicaiton."""


import cStringIO
from xml.dom import minidom
from xml.sax.saxutils import XMLGenerator

from django.contrib import admin
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.core.serializers.xml_serializer import getInnerText

from cms.apps.versions.models import Version


class VersionAdmin(admin.ModelAdmin):
    
    """Base class for models that wish to take advantage of version control."""
    
    def serialize(self, obj):
        """Serializes the given object version objects."""
        # Start the XML document.
        out = cStringIO.StringIO()
        generator = XMLGenerator(out, "utf-8")
        generator.startDocument()
        generator.startElement("version", {})
        # Generate the XML.
        # TODO: Re-implement this!
        for field in self.fields:
            key = field.name
            value = self.data[key]
            generator.startElement("property", {"name": key})
            if value is None:
                serialized_value = ""
            else:
                serialized_value = field.serialize(value)
            generator.characters(serialized_value)
            generator.endElement("property")
        # Return the generated XML.
        generator.endElement("version")
        generator.endDocument()
        return out.getvalue()
    
    def log_addition(self, request, obj):
        """Log that an object has been successfully added."""
        log_entry = LogEntry.objects.create(user_id=request.user.pk, 
                                            content_type_id=ContentType.objects.get_for_model(obj).pk,
                                            object_id=obj.pk,
                                            object_repr=unicode(obj), 
                                            action_flag=ADDITION)
        #Version.objects.create(log_entry=log_entry, data=self.serialize(obj))
        
    def log_change(self, request, obj, message):
        """Log that an object has been successfully changed."""
        log_entry = LogEntry.objects.create(user_id=request.user.pk, 
                                            content_type_id=ContentType.objects.get_for_model(obj).pk, 
                                            object_id=obj.pk, 
                                            object_repr=unicode(obj), 
                                            action_flag=CHANGE, 
                                            change_message=message)
        #Version.objects.create(log_entry=log_entry, data=self.serialize(obj))
        
        