"""
Generic serialization framework.

This is not a duplication of the Django serialization framework, which deals
only with models.  Rather, this is a way of serializing abstract Python types
into XML for database storage.
"""


import cStringIO, datetime
from xml.dom import minidom

from django.conf import settings
from django.db import models
from django.utils.xmlutils import SimplerXMLGenerator


class Codec(object):
    
    """
    A plugable codec that knows how to serialize and deserialize a particular
    Python type.
    
    Subclasses should extend this by overriding the two methods defined below.
    """
    
    def __init__(self, serializer):
        """Initializes the Codec."""
        self.serializer = serializer
    
    def encode(self, obj, generator):
        """Encodes the given object into an XML document."""
        generator.characters(str(obj))
    
    def get_unicode(self, node):
        """Returns the unicode text content of a node."""
        text = []
        for child in node.childNodes:
            if child.nodeType == child.TEXT_NODE or child.nodeType == child.CDATA_SECTION_NODE:
                text.append(child.data)
            elif child.nodeType == child.ELEMENT_NODE:
                text.extend(self.get_text(child))
            else:
               pass
        return u"".join(text)
    
    def get_text(self, node):
        """Returns the text content of a node."""
        return str(self.get_unicode(node))
    
    def get_child(self, node, tagname):
        """Returns the first child node with the given name."""
        return node.getElementsByTagName(tagname)[0]
    
    def get_child_unicode(self, node, tagname):
        """Returns the unicode content of the named child node."""
        return self.get_unicode(self.get_child(node, tagname))
    
    def get_child_text(self, node, tagname):
        """Returns the text content of the named child node."""
        return self.get_text(self.get_child(node, tagname))
    
    def decode(self, node):
        """Converts the given node into an object."""
        return self.get_text(node)
    
    
class StringCodec(Codec):
    
    """A codec for string objects."""
    
    
class UnicodeCodec(Codec):
    
    """A codec for unicode objects."""
    
    def encode(self, obj, generator):
        """Encodes the unicode object."""
        generator.characters(obj.encode(self.serializer.encoding))
        
    def decode(self, node):
        """Decodes the given node into a string."""
        return self.get_unicode(node)
    
    
class IntCodec(Codec):
    
    """A codec for int objects."""
    
    def decode(self, node):
        """Decodes the node into an integer."""
        return int(self.get_text(node))
    
    
class FloatCodec(Codec):
    
    """A codec for float objects."""
    
    def decode(self, node):
        """Decodes the node into a float."""
        return float(self.get_text(node))
    
    
class DateCodec(Codec):
    
    """A codec for date objects."""
    
    def encode(self, obj, generator):
        """Encodes the date object."""
        generator.addQuickElement("year", str(obj.year))
        generator.addQuickElement("month", str(obj.month))
        generator.addQuickElement("day", str(obj.day))
        
    def decode(self, node):
        """Decodes the node into a date object."""
        year = int(self.get_child_text(node, "year"))
        month = int(self.get_child_text(node, "month"))
        day = int(self.get_child_text(node, "day"))
        return datetime.date(year, month, day)
        
        
class DateTimeCodec(DateCodec):
    
    """A codec for datetime objects."""
    
    def encode(self, obj, generator):
        """Encodes the datetime object."""
        super(DateTimeCodec, self).encode(obj, generator)
        generator.addQuickElement("hour", str(obj.hour))
        generator.addQuickElement("minute", str(obj.minute))
        generator.addQuickElement("second", str(obj.second))
        generator.addQuickElement("microsecond", str(obj.microsecond))
    
    def decode(self, node):
        """Decodes the node into a datetime objects."""
        date = super(DateTimeCodec, self).decode(node)
        hour = int(self.get_child_text(node, "hour"))
        minute = int(self.get_child_text(node, "minute"))
        second = int(self.get_child_text(node, "second"))
        microsecond = int(self.get_child_text(node, "microsecond"))
        return datetime.datetime(date.year, date.month, date.day, hour, minute, second, microsecond)
    
    
class ModelCodec(Codec):
    
    """A codec for Django models."""
    
    def encode(self, obj, generator):
        """Encodes the Django model instance."""
        generator.addQuickElement("app-label", str(obj._meta.app_label))
        generator.addQuickElement("model", obj.__class__.__name__.lower())
        generator.addQuickElement("pk", str(obj.pk))


class ListCodec(Codec):
    
    """A codec for list objects."""
    
    def encode(self, obj, generator):
        """Encodes the sequence."""
        for item in obj:
            self.serializer.encode(item, generator)
            
    def decode(self, node):
        """Decodes the node into a list."""
        result = [self.serializer.decode(node)
                  for node in node.getElementsByTagName("obj")]
        return result
    
    
class TupleCodec(ListCodec):
    
    """A codec for tuple objects."""
    
    def decode(self, node):
        """Decodes the node into a tuple."""
        return tuple(super(TupleCodec, self).decode(node))
    
    
class SetCodec(ListCodec):
    
    """A codec for set objects."""
    
    def decode(self, node):
        """Decodes the node into a set."""
        return set(super(SetCodec, self).decode(node))
    
    
class DictCodec(Codec):
    
    """A codec for dict objects."""
    
    def encode(self, obj, generator):
        """Encodes the dict."""
        for key, value in obj.items():
            generator.startElement("item", {})
            self.serializer.encode(key, generator)
            self.serializer.encode(value, generator)
            generator.endElement("item")
            
    def decode(self, node):
        """Decodes the node into a dict."""
        result = {}
        for item in node.getElementsByTagName("item"):
            objects = item.getElementsByTagName("obj")
            key = self.serializer.decode(objects[0])
            value = self.serializer.decode(objects[1])
            result[key] = value
        return result
    
    
class SerializationError(Exception):
    
    """Error raised when something goes wrong with serialization."""
    
    
class Serializer(object):
    
    """A serializer of Python types."""
    
    def __init__(self, encoding=None):
        """Initializes the serializer."""
        self.encoding = encoding or settings.DEFAULT_CHARSET
        self._codecs = []
        
    def register_codec(self, type, codec, identifier=None):
        """Registers the given codec with this serializer."""
        identifier = identifier or type.__name__.lower()
        codec_instance = codec(self)
        self._codecs.append((type, codec_instance, identifier))
        
    def encode(self, obj, generator):
        """Encodes the given object into an XML document."""
        for type, codec, identifier in reversed(self._codecs):
            if isinstance(obj, type):
                generator.startElement("obj", {"type": identifier})
                codec.encode(obj, generator)
                generator.endElement("obj")
                return
        raise SerializationError, "No suitable codec found for type %r." % obj.__class__.__name__
        
    def decode(self, node):
        """Converts the given data from node into an object."""
        node_type = node.attributes["type"].nodeValue
        for type, codec, identifier in reversed(self._codecs):
            if node_type == identifier:
                return codec.decode(node)
        raise SerializationError, "No suitable codec found for type %r." % node_type
        
    def serialize(self, obj):
        """Serializes the given object into a string."""
        out = cStringIO.StringIO()
        generator = SimplerXMLGenerator(out, self.encoding)
        generator.startDocument()
        self.encode(obj, generator)
        generator.endDocument()
        return out.getvalue()
        
    def deserialize(self, data):
        """Deserializes the given string into an object.""" 
        document = minidom.parseString(data)
        return self.decode(document.documentElement)
        
        
# A shared serialization object.
serializer = Serializer()


# Register some default codecs.
serializer.register_codec(str, StringCodec)

serializer.register_codec(unicode, UnicodeCodec)

serializer.register_codec(int, IntCodec)

serializer.register_codec(float, FloatCodec)

serializer.register_codec(datetime.date, DateCodec)

serializer.register_codec(datetime.datetime, DateTimeCodec)

serializer.register_codec(models.Model, ModelCodec)

serializer.register_codec(list, ListCodec)

serializer.register_codec(tuple, TupleCodec)

serializer.register_codec(set, SetCodec)

serializer.register_codec(dict, DictCodec)

