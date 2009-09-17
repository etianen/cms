"""Simple library for handling XML data."""


from __future__ import absolute_import


import xml.parsers.expat


class Element(object):
    
    """An XML element."""
    
    __slots__ = ("name", "attrs", "children",)
    
    def __init__(self, name, attrs=None):
        """Initializes the Element."""
        self.name = name
        self.attrs = attrs or {}
        self.children = []
        
    def value(self):
        """Returns the text content of this element."""
        return u"".join(unicode(child) for child in self.children)
    
    def __unicode__(self):
        """Returns the element and all children encoded as XML."""
        attrs = u"".join(u' %s="%s"' % (name, value) for name, value in self.attrs.iteritems())
        value = self.value()
        data = {"name": self.name,
                "attrs": attrs,
                "value": value}
        if value:
            return u"<%(name)s%(attrs)s>%(value)s</%(name)s>" % data
        return u"<%(name)s%(attrs)s/>" % data


class XML(object):
    
    """Some queryable XML data."""
    
    __slots__ = ("elements",)
    
    def __init__(self, elements):
        """Initializes the XML object."""
        self.elements = elements
        
    def __unicode__(self):
        """Returns a unicode representation of this XML data."""
        return u"".join(unicode(element) for element in self.elements)
    

class SimpleContentHandler(object):
    
    """
    A SAX handler for parsing XML data.
    
    Once the parse has finished, it will have an `xml` property corresponding
    to the root element of the parsed XML elements.
    """
    
    def __init__(self):
        """Initializes the SimpleContentHandler."""
        self.stack = [] 
    
    def startElement(self, name, attrs):
        """Registers the start of an element."""
        self.stack.append(Element(name, attrs))
        
    def endElement(self, name):
        """Registers the end of an element."""
        element = self.stack.pop()
        if self.stack:
            self.stack[-1].children.append(element)
        else:
            self.xml = XML([element])
            
    def characters(self, content):
        """Registers some character data."""
        self.stack[-1].children.append(content)

        
def parse(data):
    """Parses the given data and returns an XML object."""
    parser = xml.parsers.expat.ParserCreate()
    handler = SimpleContentHandler()
    parser.StartElementHandler = handler.startElement
    parser.EndElementHandler = handler.endElement
    parser.CharacterDataHandler = handler.characters
    if isinstance(data, basestring):
        parser.Parse(data, True)
    elif hasattr(data, "read"):
        parser.ParseFile(data)
    else:
        raise TypeError, "Data should be a string or file-like object, not a %s" % type(data).__name__
    return handler.xml
    
    