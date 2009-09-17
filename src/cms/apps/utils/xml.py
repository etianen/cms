"""Simple library for handling XML data."""


from __future__ import absolute_import

import sys
import xml.parsers.expat


class Element(object):
    
    """An XML element."""
    
    __slots__ = ("name", "attrs", "children",)
    
    def __init__(self, name, attrs=None):
        """Initializes the Element."""
        self.name = name
        self.attrs = attrs or {}
        self.children = []
        
    def get_value(self):
        """Returns the text content of this element."""
        return u"".join(unicode(child) for child in self.children)
    
    def __unicode__(self):
        """Returns the element and all children encoded as XML."""
        attrs = u"".join(u' %s="%s"' % (name, value) for name, value in self.attrs.iteritems())
        value = self.get_value()
        data = {"name": self.name,
                "attrs": attrs,
                "value": value}
        if value:
            return u"<%(name)s%(attrs)s>%(value)s</%(name)s>" % data
        return u"<%(name)s%(attrs)s/>" % data
    
    def __str__(self):
        """Returns an encoded representation of this element."""
        return unicode(self).encode(sys.getdefaultencoding(), "xmlcharrefreplace")


class XML(object):
    
    """Some queryable XML data."""
    
    __slots__ = ("_elements",)
    
    def __init__(self, elements):
        """Initializes the XML object."""
        self._elements = elements
        
    def get_value(self):
        """Returns the text content of the first matched element."""
        return self._elements[0].get_value()
    
    value = property(get_value,
                     doc="The text content of the first matched element.")
        
    def get_all_values(self):
        """Returns a list of the text content of all matched elements."""
        return [element.get_value() for element in self._elements]
        
    all_values = property(get_all_values,
                          doc="A list of all the text content of all matched elements.")
        
    def get_name(self):
        """Returns the name of the first matched element."""
        return self._elements[0].name
    
    name = property(get_name,
                    doc="The name of the first matched element.")
    
    def get_attrs(self):
        """Returns the attributes of the first matched element."""
        return self._elements[0].attrs
    
    attrs = property(get_attrs,
                     doc="The attributes of the first matched element.")
    
    def _iter(self, elements, depth=-1):
        """
        Recursively iterates over all the given elements and their children.
        
        If depth is given, then this will limit the recursion.  A depth of -1
        (the default) implies infinite recursion.
        """
        for element in elements:
            # Ignore character data.
            if isinstance(element, basestring):
                continue
            yield element
            if depth != 0:
                for child in self._iter(element.children, depth - 1):
                    yield child
    
    def _filter(self, elements, args):
        """Filters the given elements using the given criteria."""
        args = frozenset(args)
        matches = set()  # Used to ensure unique results.
        for element in elements:
            # Ignore if already matched.
            if element in matches:
                continue
            else:
                matches.add(element)
            # Ignore if not in list of valid names.
            if args and not element.name in args:
                continue
            yield element
    
    def filter(self, *args):
        """
        Returns a filtered version of this XML.
        
        This method is passed a series of element names, and only the matched
        elements will be returned as a new XML object.  All descendents of
        matched elements will be matched.  If you only wish to match direct
        descendents, use the `children` method.
        """
        return XML(list(self._filter(self._iter(self._elements), args)))
        
    def children(self, *args):
        """
        Returns a filtered view of direct children of matched elements.
        
        Please see the documentation for `filter` for more information.
        """
        return XML(list(self._filter(self._iter(self._elements, 1), args)))
    
    def __unicode__(self):
        """Returns a unicode representation the first matched element."""
        return unicode(self._elements[0])
    
    def __str__(self):
        """Returns an encoded representation of the first matched element."""
        return str(self._elements[0])
    
    def __len__(self):
        """Returns the number of matched elements."""
        return len(self._elements)
    
    def __getitem__(self, index):
        """Returns the item at the given index."""
        elements = self._elements.__getitem__(index)
        if isinstance(elements, Element):
            elements = [elements]
        return XML(elements)
    

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
    
    