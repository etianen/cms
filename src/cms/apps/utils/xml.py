"""Simple library for handling XML data."""


from __future__ import absolute_import

import sys
import xml.parsers.expat
from xml.sax.saxutils import escape, quoteattr

from django.http import HttpResponse


class Element(object):
    
    """An XML element."""
    
    __slots__ = ("name", "attrs", "children",)
    
    def __init__(self, name, attrs):
        """Initializes the Element."""
        self.name = name
        self.attrs = attrs
        self.children = []
        
    def get_value(self):
        """Returns the text content of this element."""
        return u"".join(isinstance(child, basestring) and escape(child) or unicode(child) for child in self.children)
    
    def __unicode__(self):
        """Returns the element and all children encoded as XML."""
        attrs = u"".join(u' %s="%s"' % (name, quoteattr(value)) for name, value in self.attrs.iteritems())
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


class XMLError(Exception):
    
    """Exception raised when something goes wrong with XML."""


class ParseError(XMLError):
    
    """Exception raised when an XML document cannot be parsed."""


class ElementDoesNotExist(XMLError):
    
    """
    Exception raised when an attempt is made to manipulate an XML object with
    no matched elements.
    """
    


class XML(object):
    
    """Some queryable XML data."""
    
    __slots__ = ("_elements",)
    
    def __init__(self, elements):
        """Initializes the XML object from an ordered list of elements."""
        self._elements = elements
    
    # Manipulation API.
    
    def _get_element(self):
        """Returns the first matched element."""
        try:
            return self._elements[0]
        except IndexError:
            raise ElementDoesNotExist, "There are no matched elements."""
        
    def get_value(self):
        """Returns the text content of the first matched element."""
        return self._get_element().get_value()
    
    def set_value(self, value):
        """Sets the text content of the first matched element."""
        self._get_element().children = [value,]
    
    value = property(get_value,
                     doc="The text content of the first matched element.")
        
    def get_name(self):
        """Returns the name of the first matched element."""
        return self._get_element().name
    
    def set_name(self, name):
        """Sets the name of the first matched element."""
        self._get_element().name = name 
    
    name = property(get_name,
                    set_name,
                    doc="The name of the first matched element.")
    
    def get_attrs(self):
        """Returns the attributes of the first matched element."""
        return self._get_element().attrs
    
    def set_attrs(self, attrs):
        """Sets the attributes of the first matched element."""
        self._get_element().attrs = attrs
    
    attrs = property(get_attrs,
                     set_attrs,
                     doc="The attributes of the first matched element.")
    
    def append(self, element_name, *content, **attrs):
        """
        Appends a new element to the first matched element.
        
        The new element is returned.
        """
        element = Element(element_name, attrs)
        element.children.extend(content)
        self._get_element().children.append(element)
        return XML((element),)
        
    
    # Search API.
    
    def _filter(self, names, elements):
        """
        Filters the given elements using the given criteria and returns an XML
        object.
        """
        names = frozenset(names)
        known_elements = set()  # Ensures uniquenes of results.
        matches = []
        for element in elements:
            if element in known_elements:
                continue
            if not names or element.name in names:
                matches.append(element)
        return XML(matches)
    
    def _iter_elements(self, elements):
        """
        Recursively iterates over all the given elements and their children.
        
        If depth is given, then this will limit the recursion.  A depth of -1
        (the default) implies infinite recursion.
        """
        for element in elements:
            # Ignore character data.
            if isinstance(element, basestring):
                continue
            # Iterate ove element and children.
            yield element
            for child in self._iter_elements(element.children):
                yield child
    
    def filter(self, *names):
        """
        Returns a filtered version of this XML.
        
        This method is passed a series of element names, and only the matched
        elements will be returned as a new XML object.  All descendents of
        matched elements will be matched.  If you only wish to match direct
        descendents, use the `children` method.
        """
        return self._filter(names, self._iter_elements(self._elements))
        
    def children(self, *names):
        """
        Returns a filtered view of direct children of matched elements.
        
        Please see the documentation for `filter` for more information.
        """
        children = (child for element in self._elements if not isinstance(element, unicode)
                          for child in element.children if not isinstance(child, unicode))
        return self._filter(names, children)
    
    def __len__(self):
        """Returns the number of matched elements."""
        return len(self._elements)
    
    def __getitem__(self, index):
        """Returns the item at the given index."""
        elements = self._elements.__getitem__(index)
        if isinstance(elements, Element):
            elements = [elements]
        return XML(elements)
    
    # Output API.
    
    def __unicode__(self):
        """Returns a unicode representation the first matched element."""
        return unicode(self._get_element())
    
    def __str__(self):
        """Returns an encoded representation of the first matched element."""
        return str(self._get_element())
    
    def render(self, encoding="utf-8"):
        """Writes the first matched element as an encoded XML document."""
        preamble = "<?xml version=\"1.0\" encoding=\"%s\"?>\n" % encoding
        return preamble + unicode(self).encode(encoding, "xmlcharrefreplace")
    
    def render_to_response(self, encoding="utf-8"):
        """Renders the first matched element to a HttpResponse."""
        return HttpResponse(self.render(encoding), content_type="application/xml; charset=%s" % encoding)
    

class SimpleContentHandler(object):
    
    """
    A SAX handler for parsing XML data.
    
    Once the parse has finished, it will have an `xml` property corresponding
    to the root element of the parsed XML.
    """
    
    def __init__(self):
        """Initializes the SimpleContentHandler."""
        self.stack = []
    
    def startElement(self, name, attrs):
        """Registers the start of an element."""
        element = Element(name, attrs)
        self.stack.append(element)
        
    def endElement(self, name):
        """Registers the end of an element."""
        element = self.stack.pop()
        if self.stack:
            self.stack[-1].children.append(element)
        else:
            self.xml = XML((element,))
            
    def characters(self, content):
        """Registers some character data."""
        self.stack[-1].children.append(content)

        
def parse(data):
    """Parses the given data and returns an XML object."""
    # Load the data.
    if isinstance(data, basestring):
        pass
    elif hasattr(data, "read"):
        data = data.read()
    else:
        raise TypeError, "Data should be a string or file-like object, not a %s" % type(data).__name__
    # Set up a parser.
    parser = xml.parsers.expat.ParserCreate()
    handler = SimpleContentHandler()
    parser.StartElementHandler = handler.startElement
    parser.EndElementHandler = handler.endElement
    parser.CharacterDataHandler = handler.characters
    try:
        parser.Parse(data, True)
    except xml.parsers.expat.ExpatError, ex:
        snippet = "... %s ..." % data.splitlines()[ex.lineno-1][ex.offset-30:ex.offset+30]
        raise ParseError, snippet
    return handler.xml


def create(name, *content, **attrs):
    """Creates a new XML document with the given root element."""
    element = Element(name, attrs)
    element.children.extend(content)
    return XML((element,))
        
    