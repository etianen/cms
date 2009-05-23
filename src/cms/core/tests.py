"""Tests for core CMS functionality."""


import datetime, unittest

from django.contrib.contenttypes.models import ContentType

from cms.core.serializers import serializer


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

    
    def testSerialize(self):
        """
        Ensure that encoding and decoding are reversible for a variety of test
        cases.
        """
        for obj in self.examples:
            serialized = serializer.serialize(obj)
            deserialized = serializer.deserialize(serialized)
            self.assertEqual(obj, deserialized)
            
            