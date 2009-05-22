"""Tests for core CMS functionality."""


import datetime, unittest

from cms.core.serializers import serializer


class TestSerializer(unittest.TestCase):
    
    """Tests the serialization framework."""
    
    examples = (("hello world",
                 '<?xml version="1.0" encoding="utf-8"?>\n'
                 '<obj type="str">hello world</obj>'),
                (u"hello world",
                 '<?xml version="1.0" encoding="utf-8"?>\n'
                 '<obj type="unicode">hello world</obj>'),
                (5,
                 '<?xml version="1.0" encoding="utf-8"?>\n'
                 '<obj type="int">5</obj>'),
                (5.0,
                 '<?xml version="1.0" encoding="utf-8"?>\n'
                 '<obj type="float">5.0</obj>'),
                (datetime.date(1984, 5, 19),
                 '<?xml version="1.0" encoding="utf-8"?>\n'
                 '<obj type="date">'
                 '<year>1984</year>'
                 '<month>5</month>'
                 '<day>19</day>'
                 '</obj>'),
                (datetime.datetime(1984, 5, 19, 3, 35, 55),
                 '<?xml version="1.0" encoding="utf-8"?>\n'
                 '<obj type="datetime">'
                 '<year>1984</year>'
                 '<month>5</month>'
                 '<day>19</day>'
                 '<hour>3</hour>'
                 '<minute>35</minute>'
                 '<second>55</second>'
                 '<microsecond>0</microsecond>'
                 '</obj>'),
                (["foo", 5],
                 '<?xml version="1.0" encoding="utf-8"?>\n'
                 '<obj type="list">'
                 '<obj type="str">foo</obj>'
                 '<obj type="int">5</obj>'
                 '</obj>'),
                (("foo", 5,),
                 '<?xml version="1.0" encoding="utf-8"?>\n'
                 '<obj type="tuple"><'
                 'obj type="str">foo</obj>'
                 '<obj type="int">5</obj>'
                 '</obj>',),
                (set(("foo", 5)),
                 '<?xml version="1.0" encoding="utf-8"?>\n'
                 '<obj type="set">'
                 '<obj type="str">foo</obj>'
                 '<obj type="int">5</obj>'
                 '</obj>'),
                ({"foo": "bar", "list": ["one", "two"]},
                 '<?xml version="1.0" encoding="utf-8"?>\n'
                 '<obj type="dict">'
                 '<item>'
                 '<obj type="str">foo</obj>'
                 '<obj type="str">bar</obj>'
                 '</item>'
                 '<item>'
                 '<obj type="str">list</obj>'
                 '<obj type="list">'
                 '<obj type="str">one</obj>'
                 '<obj type="str">two</obj>'
                 '</obj>'
                 '</item>'
                 '</obj>'),)
        
    def testSerialize(self):
        """Runs some examples through the serializer."""
        for obj, expected in self.examples:
            result = serializer.serialize(obj)
            self.assertEqual(result, expected)
            
    def testDeserialize(self):
        """Runs some examples through the deserializer."""
        for expected, data in self.examples:
            result = serializer.deserialize(data)
            self.assertEqual(result, expected)

        