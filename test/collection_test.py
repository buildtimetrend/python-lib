# vim: set expandtab sw=4 ts=4:
#
# Unit tests for Collection class
#
# Copyright (C) 2014 Dieter Adriaenssens <ruleant@users.sourceforge.net>
#
# This file is part of buildtime-trend
# <https://github.com/ruleant/buildtime-trend/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from buildtimetrend.collection import Collection
import unittest


class TestCollection(unittest.TestCase):
    def setUp(self):
        self.collection = Collection()

    def test_novalue(self):
        # number of items should be zero
        self.assertEquals(0, len(self.collection.items))

        # items collection should be an empty dictionary
        self.assertDictEqual({}, self.collection.get_items())

    def test_add_item(self):
        # error is thrown when called without parameters
        self.assertRaises(TypeError, self.collection.add_item)

        self.collection.add_item('property1', 2)
        self.assertEquals(1, len(self.collection.items))
        self.assertDictEqual({'property1': 2}, self.collection.items)

        self.collection.add_item('property2', 3)
        self.assertEquals(2, len(self.collection.items))
        self.assertDictEqual({'property1': 2, 'property2': 3}, self.collection.items)

        self.collection.add_item('property2', 4)
        self.assertEquals(2, len(self.collection.items))
        self.assertDictEqual({'property1': 2, 'property2': 4}, self.collection.items)

    def test_get_item(self):
        self.collection.add_item('property1', 2)
        self.assertEquals(2, self.collection.get_item('property1'))

        self.collection.add_item('property1', None)
        self.assertEquals(None, self.collection.get_item('property1'))

        self.collection.add_item('property2', 3)
        self.assertEquals(3, self.collection.get_item('property2'))

        self.collection.add_item('property2', 4)
        self.assertEquals(4, self.collection.get_item('property2'))

    def test_get_property_does_not_exist(self):
        self.assertEquals(None, self.collection.get_item('no_property'))

    def test_get_items(self):
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
