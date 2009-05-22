"""
Generic serialization framework.

This is not a duplication of the Django serialization framework, which deals
only with models.  Rather, this is a way of serializing abstract Python types
into XML for database storage.
"""


import cStringIO, datetime
from xml.dom import pulldom

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
    
    def decode(self, node, events):
        """Converts the given node into an object."""
        raise NotImplementedError
    
    
class StringCodec(Codec):
    
    """A codec for string objects."""
    
    
class UnicodeCodec(Codec):
    
    """A codec for unicode objects."""
    
    
class IntCodec(Codec):
    
    """A codec for int objects."""
    
    def decode(self, node, events):
        """Decodes the nodes into an integer."""
    
    
class FloatCodec(Codec):
    
    """A codec for float objects."""
    
    
class DateCodec(Codec):
    
    """A codec for date objects."""
    
    def encode(self, obj, generator):
        """Encodes the date object."""
        generator.addQuickElement("year", str(obj.year))
        generator.addQuickElement("month", str(obj.month))
        generator.addQuickElement("day", str(obj.day))
        
        
class DateTimeCodec(DateCodec):
    
    """A codec for datetime objects."""
    
    def encode(self, obj, generator):
        """Encodes the datetime object."""
        super(DateTimeCodec, self).encode(obj, generator)
        generator.addQuickElement("hour", str(obj.hour))
        generator.addQuickElement("minute", str(obj.minute))
        generator.addQuickElement("second", str(obj.second))
        generator.addQuickElement("microsecond", str(obj.microsecond))
    
    
class ModelCodec(Codec):
    
    """A codec for Django models."""
    
    def encode(self, obj, generator):
        """Encodes the Django model instance."""
        generator.addQuickElement("app-label", str(obj._meta.app_label))
        generator.addQuickElement("model", obj.__class__.__name__.lower())
        generator.addQuickElement("pk", str(obj.pk))


class DictCodec(Codec):
    
    """A codec for dict objects."""
    
    def encode(self, obj, generator):
        """Encodes the dict."""
        for key, value in obj.items():
            generator.startElement("item", {})
            self.serializer.encode(key, generator)
            self.serializer.encode(value, generator)
            generator.endElement("item")
    
    
class SequenceCodec(Codec):
    
    """A base codec for list, tuple and set objects."""
    
    def encode(self, obj, generator):
        """Encodes the sequence."""
        for item in obj:
            self.serializer.encode(item, generator)
    
    
class ListCodec(SequenceCodec):
    
    """A codec for list objects."""
    
    
class TupleCodec(SequenceCodec):
    
    """A codec for tuple objects."""
    
    
class SetCodec(SequenceCodec):
    
    """A codec for set objects."""
    
    
class SerializationError(Exception):
    
    """Error raised when something goes wrong with serialization."""
    
    
class Serializer(object):
    
    """A serializer of Python types."""
    
    def __init__(self, encoding="utf8"):
        """Initializes the serializer."""
        self._codecs = []
        self.encoding = encoding
        
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
        
    def decode(self, events):
        """Converts the given data from node into an object."""
        for event, node in events:
            if event == "START_ELEMENT" and node.nodeName == "obj":
                node_type = node.attributes["type"]
                for type, codec, identifier in reversed(self._codecs):
                    if node_type == identifier:
                        return codec.decode(node, events)
            
        
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
        events = pulldom.parseString(data)
        return self.decode(events)
        
        
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

serializer.register_codec(dict, DictCodec)

serializer.register_codec(list, ListCodec)

serializer.register_codec(tuple, TupleCodec)

serializer.register_codec(set, SetCodec)

