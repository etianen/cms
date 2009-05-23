"""Tests for core CMS functionality."""


import datetime, unittest

from django.contrib.contenttypes.models import ContentType

from cms.core.optimizations import cached_property
from cms.core.serializers import serializer


# Test the optimizations.


class CachedPropertyTest(object):
    
    """Used to test the cached_property optimization."""
    
    def __init__(self):
        self.call_count = 0
        self._value = "initial"
        
    def get_value(self):
        self.call_count += 1
        return self._value
    
    def set_value(self, value):
        self._value = value
        
    def del_value(self):
        del self._value
        
    value = cached_property(get_value,
                            set_value,
                            del_value)
    
    
class TestCachedProperty(unittest.TestCase):
    
    """Tests the cached_property optimization."""
    
    def setUp(self):
        """Sets up a CachedPropertyTest object."""
        self.cached_property_test = CachedPropertyTest()
    
    def testGetterIsCached(self):
        """Tests that calls to getters are cached."""
        self.cached_property_test.value
        self.assertEqual(self.cached_property_test.call_count, 1)
        self.cached_property_test.value
        self.assertEqual(self.cached_property_test.call_count, 1)
        
    def testSetterSetsCache(self):
        """Tests that calls to setters sets the cache."""
        self.cached_property_test.value = "changed"
        self.assertEqual(self.cached_property_test.value, "changed")
        self.assertEqual(self.cached_property_test.call_count, 0)
        
    def testDeleterClearsCache(self):
        """Tests that calls to deleters clear the cache."""
        self.cached_property_test.value
        del self.cached_property_test.value
        self.assertRaises(AttributeError, lambda: self.cached_property_test.value)
        self.cached_property_test.value = "changed"
        self.assertEqual(self.cached_property_test.call_count, 2)
        

# Test the serialization.


class TestSerializer(unittest.TestCase):
    
    """Tests the serialization framework."""
    
    examples = (u"hello world",
                "hello world",
                5,
                6L,
                5.5,
                datetime.date(1984, 5, 19),
                datetime.datetime(1984, 5, 19, 3, 35, 55),
                ContentType.objects.all()[0],
                ["foo", 5],
                set(("foo", 5)),
                {"foo": "bar", "list": ["one", "two"]},)

    
    def testSerializationIsReversible(self):
        """
        Tests that encoding and decoding are reversible for a variety of test
        cases.
        """
        for obj in self.examples:
            serialized = serializer.serialize(obj)
            deserialized = serializer.deserialize(serialized)
            self.assertEqual(obj, deserialized)
            
            