# vim: set expandtab sw=4 ts=4:
#
# Unit tests for Collection class
#
# Copyright (C) 2014-2015 Dieter Adriaenssens <ruleant@users.sourceforge.net>
#
# This file is part of buildtimetrend/python-lib
# <https://github.com/buildtimetrend/python-lib/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from buildtimetrend.collection import Collection
import unittest


class TestCollection(unittest.TestCase):

    """Unit tests for Collection class"""

    def setUp(self):
        """Set up test fixture."""
        self.collection = Collection()

    def test_novalue(self):
        """Test freshly initialised object."""
        # number of items should be zero
        self.assertEqual(0, len(self.collection.items))

        # items collection should be an empty dictionary
        self.assertDictEqual({}, self.collection.get_items())

    def test_add_item(self):
        """Test add_item()"""
        # error is thrown when called without parameters
        self.assertRaises(TypeError, self.collection.add_item)

        self.collection.add_item('property1', 2)
        self.assertEqual(1, len(self.collection.items))
        self.assertDictEqual({'property1': 2}, self.collection.items)

        self.collection.add_item('property2', 3)
        self.assertEqual(2, len(self.collection.items))
        self.assertDictEqual({'property1': 2, 'property2': 3},
                             self.collection.items)

        self.collection.add_item('property2', 4)
        self.assertEqual(2, len(self.collection.items))
        self.assertDictEqual({'property1': 2, 'property2': 4},
                             self.collection.items)

    def test_get_size(self):
        """Test get_size()"""
        self.collection.add_item('property1', 2)
        self.assertEqual(1, len(self.collection.items))
        self.assertEqual(1, self.collection.get_size())

        self.collection.add_item('property2', 3)
        self.assertEqual(2, len(self.collection.items))
        self.assertEqual(2, self.collection.get_size())

        self.collection.add_item('property2', 4)
        self.assertEqual(2, len(self.collection.items))
        self.assertEqual(2, self.collection.get_size())

    def test_get_item(self):
        """Test get_item()"""
        self.collection.add_item('property1', 2)
        self.assertEqual(2, self.collection.get_item('property1'))

        self.collection.add_item('property1', None)
        self.assertEqual(None, self.collection.get_item('property1'))

        self.collection.add_item('property2', 3)
        self.assertEqual(3, self.collection.get_item('property2'))

        self.collection.add_item('property2', 4)
        self.assertEqual(4, self.collection.get_item('property2'))

    def test_get_property_does_not_exist(self):
        """Test get_item() for non-existing item"""
        self.assertEqual(None, self.collection.get_item('no_property'))

    def test_add_items_invalidparameter(self):
        """Test add_item() with invalid parameters"""
        # error is thrown when called without parameters
        self.assertRaises(TypeError, self.collection.add_items)

        # error is thrown when called with an invalid parameter
        self.assertRaises(TypeError, self.collection.add_items, None)
        self.assertRaises(TypeError, self.collection.add_items, "string")
        self.assertRaises(TypeError, self.collection.add_items, 1234)

    def test_add_items(self):
        """Test add_items()"""
        # add item to empty collection
        self.collection.add_items({'property1': 2})
        self.assertDictEqual(
            {'property1': 2},
            self.collection.get_items())

        # add nonexistant item to an existing collection
        self.collection.add_items({'property2': 3})
        self.assertDictEqual(
            {'property1': 2, 'property2': 3},
            self.collection.get_items())

        # add existant item with different value to an existing collection
        self.collection.add_items({'property2': 4})
        self.assertDictEqual(
            {'property1': 2, 'property2': 4},
            self.collection.get_items())

    def test_add_items_multiple(self):
        """Test add_items() with multiple items at once"""
        # fill collection with items
        self.collection.add_item('property1', 2)
        self.collection.add_item('property2', 3)

        # add items (existing and new)
        self.collection.add_items({
            'property2': 4,
            'property3': 6
        })

        # assert items collection
        self.assertDictEqual(
            {
                'property1': 2,
                'property2': 4,
                'property3': 6
            },
            self.collection.get_items()
        )

    def test_get_items(self):
        """Test get_items()"""
        self.collection.add_item('property1', 2)
        self.assertDictEqual(
            {'property1': 2},
            self.collection.get_items())

        self.collection.add_item('property2', 3)
        self.assertDictEqual(
            {'property1': 2, 'property2': 3},
            self.collection.get_items())

        self.collection.add_item('property2', 4)
        self.assertDictEqual(
            {'property1': 2, 'property2': 4},
            self.collection.get_items())

    def test_get_items_with_summary(self):
        """Test get_items_with_summary()"""
        self.collection.add_item('property1', '2')
        self.assertDictEqual(
            {'property1': '2'},
            self.collection.get_items())
        self.assertDictEqual(
            {'property1': '2', 'summary': '2'},
            self.collection.get_items_with_summary())

        self.collection.add_item('property2', '3')
        self.assertDictEqual(
            {'property1': '2', 'property2': '3'},
            self.collection.get_items())
        self.assertDictEqual(
            {
                'property1': '2', 'property2': '3',
                'summary': '2 3'
            },
            self.collection.get_items_with_summary())

        self.collection.add_item('property2', '4')
        self.assertDictEqual(
            {'property1': '2', 'property2': '4'},
            self.collection.get_items())
        self.assertDictEqual(
            {
                'property1': '2', 'property2': '4',
                'summary': '2 4'
            },
            self.collection.get_items_with_summary())

        self.collection.add_item('property2', 5)
        self.assertDictEqual(
            {'property1': '2', 'property2': 5},
            self.collection.get_items())
        # summary is only available if all properties have string values
        self.assertDictEqual(
            {'property1': '2', 'property2': 5},
            self.collection.get_items_with_summary())

    def test_get_key_sorted_items(self):
        """Test get_key_sorted_items()"""
        self.collection.add_item('property3', 2)
        self.collection.add_item('property1', 3)

        ordered_dict = self.collection.get_key_sorted_items()
        keys = list(ordered_dict.keys())
        self.assertEqual('property1', keys[0])
        self.assertEqual('property3', keys[1])

        self.collection.add_item('property2', 4)

        ordered_dict = self.collection.get_key_sorted_items()
        keys = list(ordered_dict.keys())
        self.assertEqual('property1', keys[0])
        self.assertEqual('property2', keys[1])
        self.assertEqual('property3', keys[2])
