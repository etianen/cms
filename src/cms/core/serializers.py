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
        raise NotImplementedError
        
    def decode(self, node):
        """Converts the given node into an object."""
        raise NotImplementedError
    
    
class UnicodeCodec(Codec):
    
    """A codec for unicode objects."""
    
    def encode(self, obj, generator):
        """Encodes the unicode object."""
        obj = unicode(obj)
        generator.characters(obj.encode(self.serializer.encoding))
        
    def decode(self, node):
        """Decodes the given node into a string."""
        text = []
        for child in node.childNodes:
            if child.nodeType == child.TEXT_NODE or child.nodeType == child.CDATA_SECTION_NODE:
                text.append(child.data)
            elif child.nodeType == child.ELEMENT_NODE:
                text.extend(self.decode(child))
        return u"".join(text)


class IntCodec(UnicodeCodec):
    
    """A codec for int objects."""
    
    def decode(self, node):
        """Decodes the node into an integer."""
        unicode_value = super(IntCodec, self).decode(node) 
        return int(unicode_value)
    
    
class LongCodec(UnicodeCodec):
    
    """A codec for long objects."""
    
    def decode(self, node):
        """Decodes the node into an long."""
        unicode_value = super(LongCodec, self).decode(node) 
        return long(unicode_value)
    
    
class FloatCodec(UnicodeCodec):
    
    """A codec for float objects."""
    
    def decode(self, node):
        """Decodes the node into a float."""
        unicode_value = super(FloatCodec, self).decode(node) 
        return float(unicode_value)


class PropertyCodec(Codec):
    
    """
    A codec for objects that can be serialized to a dictionary of strings mapped
    to objects.
    """
    
    def encode(self, obj, generator):
        """Serializes a dictionary of string keys mapped to string values."""
        for key, value in obj.items():
            generator.startElement(key, {})
            self.serializer.encode(value, generator)
            generator.endElement(key)
            
    def decode(self, node):
        """
        Decodes the node into a dictionary of string keys mapped to values.
        """
        decoded = {}
        for child in node.childNodes:
            if child.nodeType == child.ELEMENT_NODE:
                key = child.nodeName
                value = self.serializer.decode(child.getElementsByTagName("obj")[0])
                decoded[key] = value
        return decoded
    
    
class DateCodec(PropertyCodec):
    
    """A codec for date objects."""
    
    def encode(self, obj, generator):
        """Encodes the date object."""
        encoded = {"year": obj.year,
                   "month": obj.month,
                   "day": obj.day}
        super(DateCodec, self).encode(encoded, generator)
        
    def decode(self, node):
        """Decodes the node into a date object."""
        decoded = super(DateCodec, self).decode(node)
        year = decoded["year"]
        month = decoded["month"]
        day = decoded["day"]
        return datetime.date(year, month, day)
                
     
class DateTimeCodec(PropertyCodec):
    
    """A codec for datetime objects."""
    
    def encode(self, obj, generator):
        """Encodes the datetime object."""
        encoded = {"year": obj.year,
                   "month": obj.month,
                   "day": obj.day,
                   "hour": obj.hour,
                   "minute": obj.minute,
                   "second": obj.second,
                   "microsecond": obj.microsecond}
        super(DateTimeCodec, self).encode(encoded, generator)
    
    def decode(self, node):
        """Decodes the node into a datetime objects."""
        decoded = super(DateTimeCodec, self).decode(node)
        year = decoded["year"]
        month = decoded["month"]
        day = decoded["day"]
        hour = decoded["hour"]
        minute = decoded["minute"]
        second = decoded["second"]
        microsecond = decoded["microsecond"]
        return datetime.datetime(year, month, day, hour, minute, second, microsecond)
    
    
class ModelCodec(PropertyCodec):
    
    """A codec for Django models."""
    
    def encode(self, obj, generator):
        """Encodes the Django model instance."""
        encoded = {"app-label": obj._meta.app_label,
                   "model": obj.__class__.__name__.lower(),
                   "pk": obj.pk}
        super(ModelCodec, self).encode(encoded, generator)
        
    def decode(self, node):
        """Decodes the Django model instance."""
        decoded = super(ModelCodec, self).decode(node)
        app_label = decoded["app-label"]
        model = decoded["model"]
        pk = decoded["pk"]
        model = models.get_model(app_label, model)
        return model._default_manager.get(pk=pk)


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
    
    
class DictCodec(PropertyCodec):
    
    """A codec for dict objects."""
    
    def encode(self, obj, generator):
        """Encodes the dict."""
        for key, value in obj.items():
            generator.startElement("item", {})
            encoded = {"key": key,
                       "value": value}
            super(DictCodec, self).encode(encoded, generator)
            generator.endElement("item")
            
    def decode(self, node):
        """Decodes the node into a dict."""
        result = {}
        for item in node.getElementsByTagName("item"):
            decoded = super(DictCodec, self).decode(item)
            key = decoded["key"]
            value = decoded["value"]
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
serializer.register_codec(basestring, UnicodeCodec)

serializer.register_codec(int, IntCodec)

serializer.register_codec(long, LongCodec)

serializer.register_codec(float, FloatCodec)

serializer.register_codec(datetime.date, DateCodec)

serializer.register_codec(datetime.datetime, DateTimeCodec)

serializer.register_codec(models.Model, ModelCodec)

serializer.register_codec(list, ListCodec)

serializer.register_codec(tuple, TupleCodec)

serializer.register_codec(set, SetCodec)

serializer.register_codec(dict, DictCodec)

