"""
Generic serialization framework.

This is not a duplication of the Django serialization framework, which deals
only with models.  Rather, this is a way of serializing abstract Python types
into XML for database storage.
"""


import cStringIO, datetime
from xml.dom import minidom
from xml.sax.saxutils import XMLGenerator

from django.conf import settings
from django.db import models


class SerializationError(Exception):
    
    """Error raised when something goes wrong with serialization."""


class Encoder(object):
    
    """
    A plugable encoder that knows how to serialize and deserialize a particular
    Python type.
    
    Subclasses should extend this by overriding the `can_encode`, `encode` and
    `decode` methods.
    """
    
    def __init__(self, serializer):
        """Initializes the Encoder."""
        self.serializer = serializer
    
    def can_encode(obj):
        """Tests whether this encoder can encode the given object."""
        raise NotImplementedError
    
    def write(self, obj, generator):
        """Writes the given object to the generator as character data."""
        value = unicode(obj).encode(self.serializer.encoding)
        generator.characters(value)
    
    def write_element(self, name, obj, generator):
        """
        Writes the given object to the generator as character data within the
        given node.
        """
        generator.startElement(name, {})
        self.write(obj, generator)
        generator.endElement(name)
    
    def encode_object(self, obj, generator):
        """Encodes the given object."""
        self.serializer.encode(obj, generator)
    
    def encode(self, obj, generator):
        """Encodes the given object into an XML document."""
        self.write(obj, generator)
        
    def read(self, node):
        """Reads the content of the node as a unicode object."""
        text = []
        for child in node.childNodes:
            if child.nodeType == child.TEXT_NODE or child.nodeType == child.CDATA_SECTION_NODE:
                text.append(child.data)
            elif child.nodeType == child.ELEMENT_NODE:
                text.extend(self.read(child))
        return u"".join(text)
       
    def get_elements(self, name, node):
        """Returns all the named child elements of the given node."""
        elements = [child for child in node.childNodes
                    if child.nodeType == child.ELEMENT_NODE and child.nodeName == name]
        return elements
       
    def get_element(self, name, node):
        """Returns the named child element of the given node."""
        try:
            return self.get_elements(name, node)[0]
        except IndexError:
            raise SerializationError, "Required element %r missing from %r element." % (name, node.attributes["type"])
        
    def read_element(self, name, node):
        """Reads the content of the named child node as a unicode object."""
        child = self.get_element(name, node)
        return self.read(child)
    
    def decode_objects(self, node):
        """Reads all child objects from the node."""
        objects = [self.serializer.decode(node)
                   for node in self.get_elements("obj", node)]
        return objects
        
    def decode(self, node):
        """Converts the given node into an object."""
        raise NotImplementedError
    
    
class UnicodeEncoder(Encoder):
    
    """An encoder for unicode objects."""
    
    def can_encode(self, obj):
        """This encoder is good for string types."""
        return isinstance(obj, basestring)
    
    def decode(self, node):
        """Decodes the given node into a string."""
        return self.read(node)


class IntEncoder(Encoder):
    
    """An encoder for int objects."""
    
    def can_encode(self, obj):
        """This encoder is good for integers."""
        return isinstance(obj, int)
    
    def decode(self, node):
        """Decodes the node into an integer."""
        return int(self.read(node))    
    
    
class LongEncoder(Encoder):
    
    """An encoder for long objects."""
    
    def can_encode(self, obj):
        """This encoder is good for longs."""
        return isinstance(obj, long)
    
    def decode(self, node):
        """Decodes the node into an long."""
        return long(self.read(node))
    
    
class FloatEncoder(Encoder):
    
    """An encoder for float objects."""
    
    def can_encode(self, obj):
        """This encoder is good for floats."""
        return isinstance(obj, float)
    
    def decode(self, node):
        """Decodes the node into a float."""
        return float(self.read(node))


class DateEncoder(Encoder):
    
    """An encoder for date objects."""
    
    def can_encode(self, obj):
        """This encoder is good for dates."""
        return isinstance(obj, datetime.date)
    
    def encode(self, obj, generator):
        """Encodes the date object."""
        self.write_element("year", obj.year, generator)
        self.write_element("month", obj.month, generator)
        self.write_element("day", obj.day, generator)
        
    def decode(self, node):
        """Decodes the node into a date object."""
        year = int(self.read_element("year", node))
        month = int(self.read_element("month", node))
        day = int(self.read_element("day", node))
        return datetime.date(year, month, day)
                
     
class DateTimeEncoder(Encoder):
    
    """An encoder for datetime objects."""
    
    def can_encode(self, obj):
        """This encoder is good for datetimes."""
        return isinstance(obj, datetime.datetime)
    
    def encode(self, obj, generator):
        """Encodes the datetime object."""
        self.write_element("year", obj.year, generator)
        self.write_element("month", obj.month, generator)
        self.write_element("day", obj.day, generator)
        self.write_element("hour", obj.hour, generator)
        self.write_element("minute", obj.minute, generator)
        self.write_element("second", obj.second, generator)
        self.write_element("microsecond", obj.microsecond, generator)
    
    def decode(self, node):
        """Decodes the node into a datetime objects."""
        year = int(self.read_element("year", node))
        month = int(self.read_element("month", node))
        day = int(self.read_element("day", node))
        hour = int(self.read_element("hour", node))
        minute = int(self.read_element("minute", node))
        second = int(self.read_element("second", node))
        microsecond = int(self.read_element("microsecond", node))
        return datetime.datetime(year, month, day, hour, minute, second, microsecond)
    
    
class ModelEncoder(Encoder):
    
    """An encoder for Django models."""
    
    def can_encode(self, obj):
        """This encoder is good for Django models."""
        return isinstance(obj, models.Model)
    
    def encode(self, obj, generator):
        """Encodes the Django model instance."""
        self.write_element("app-label", obj._meta.app_label, generator)
        self.write_element("model", obj.__class__.__name__.lower(), generator)
        self.write_element("pk", obj.pk, generator)
        
    def decode(self, node):
        """Decodes the Django model instance."""
        app_label = self.read_element("app-label", node)
        model = self.read_element("model", node)
        pk = self.read_element("pk", node)
        model = models.get_model(app_label, model)
        return model._default_manager.get(pk=pk)


class ListEncoder(Encoder):
    
    """An encoder for list objects."""
    
    def can_encode(self, obj):
        """This encoder is good for lists and tuples."""
        return isinstance(obj, (list, tuple))
    
    def encode(self, obj, generator):
        """Encodes the sequence."""
        for item in obj:
            self.encode_object(item, generator)
            
    def decode(self, node):
        """Decodes the node into a list."""
        return self.decode_objects(node)
    
    
class SetEncoder(ListEncoder):
    
    """An encoder for set objects."""
    
    def can_encode(self, obj):
        """This encoder is good for sets."""
        return isinstance(obj, (set, frozenset))
    
    def decode(self, node):
        """Decodes the node into a set."""
        return set(super(SetEncoder, self).decode(node))
    
    
class DictEncoder(Encoder):
    
    """An encoder for dict objects."""
    
    def can_encode(self, obj):
        """This encoder is good for dictionaries."""
        return isinstance(obj, dict)
    
    def encode(self, obj, generator):
        """Encodes the dict."""
        for key, value in obj.items():
            generator.startElement("item", {})
            self.encode_object(key, generator)
            self.encode_object(value, generator)
            generator.endElement("item")
            
    def decode(self, node):
        """Decodes the node into a dict."""
        result = {}
        for item in node.getElementsByTagName("item"):
            key, value = self.decode_objects(item)
            result[key] = value
        return result
    
    
class Serializer(object):
    
    """A serializer of Python types."""
    
    def __init__(self, encoding=None):
        """Initializes the serializer."""
        self.encoding = encoding or settings.DEFAULT_CHARSET
        self._encoders = []
        self._decoders = {}
        
    def register_encoder(self, identifier, encoder):
        """Registers the given encoder with this serializer."""
        if identifier in self._encoders:
            raise ValueError, "An encoder with that identifier has already been registered."
        encoder_instance = encoder(self)
        self._encoders.append((identifier, encoder_instance))
        self._decoders[identifier] = encoder_instance
        
    def encode(self, obj, generator):
        """Encodes the given object into an XML document."""
        for identifier, encoder in reversed(self._encoders):
            if encoder.can_encode(obj):
                generator.startElement("obj", {"type": identifier})
                encoder.encode(obj, generator)
                generator.endElement("obj")
                return
        raise SerializationError, "No suitable encoder found for type %r." % obj.__class__.__name__
        
    def decode(self, node):
        """Converts the given data from node into an object."""
        node_type = node.attributes["type"].nodeValue
        try:
            encoder = self._decoders[node_type]
        except KeyError:
            raise SerializationError, "No suitable encoder found for type %r." % node_type
        return encoder.decode(node)
        
    def serialize(self, obj):
        """Serializes the given object into a string."""
        out = cStringIO.StringIO()
        generator = XMLGenerator(out, self.encoding)
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


# Register some default encoders.
serializer.register_encoder("unicode", UnicodeEncoder)

serializer.register_encoder("int", IntEncoder)

serializer.register_encoder("long", LongEncoder)

serializer.register_encoder("float", FloatEncoder)

serializer.register_encoder("date", DateEncoder)

serializer.register_encoder("datetime", DateTimeEncoder)

serializer.register_encoder("model", ModelEncoder)

serializer.register_encoder("list", ListEncoder)

serializer.register_encoder("set", SetEncoder)

serializer.register_encoder("dict", DictEncoder)

