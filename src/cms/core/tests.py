"""Tests for core CMS functionality."""

import unittest

from django.test import TestCase

from cms.core.optimizations import CachedProperty


# Testing the optimizations module.

class OptimizationsTestObj(object):

    def __init__(self, name):
        self._name = name
        self._get_count = 0
    
    @CachedProperty
    def name(self):
        self._get_count += 1
        return self._name
        
    @name.setter
    def name(self, value):
        self._name = value
        
    @name.deleter
    def name(self):
        del self._name
        
    @CachedProperty
    def read_only(self):
        self._get_count += 1
        return "baz"


class OptimizationsTest(TestCase):

    def testCachedProperty(self):
        obj = OptimizationsTestObj("foo")
        self.assertEqual(obj._get_count, 0)
        # Call the getter.
        self.assertEqual(obj.name, "foo")
        self.assertEqual(obj._get_count, 1)
        self.assertEqual(obj.name, "foo")
        self.assertEqual(obj._get_count, 1)
        # Call the setter.
        obj.name = "bar"
        self.assertEqual(obj.name, "bar")
        self.assertEqual(obj._get_count, 1)
        # Call the deleter.
        del obj.name
        self.assertRaises(AttributeError, lambda: obj.name)
        # Call the setter again.
        obj.name = "foobar"
        self.assertEqual(obj.name, "foobar")
        self.assertEqual(obj._get_count, 2)
        # Check the read-only property.
        self.assertEqual(obj.read_only, "baz")
        self.assertEqual(obj._get_count, 3)
        self.assertEqual(obj.read_only, "baz")
        self.assertEqual(obj._get_count, 3)
        # Try modifying a read-only property.
        def set_read_only():
            obj.read_only = "foo"
        self.assertRaises(AttributeError, set_read_only)
        def del_read_only():
            del obj.read_only
        self.assertRaises(AttributeError, del_read_only)