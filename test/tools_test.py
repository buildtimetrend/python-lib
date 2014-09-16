# vim: set expandtab sw=4 ts=4:
#
# Unit tests for Tools
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

from buildtimetrend.tools import *
from buildtimetrend.settings import get_project_info
import os
import unittest
import constants

class TestTools(unittest.TestCase):
    def setUp(self):
        self.project_info = get_project_info()

    def test_format_timestamp(self):
        # test 0 timestamp (epoch)
        self.assertEquals("1970-01-01T00:00:00", format_timestamp(0))

        # test timestamp
        self.assertEquals("2014-07-09T12:38:33", format_timestamp(1404909513))

    def test_split_timestamp(self):
        # test 0 timestamp (epoch)
        self.assertDictEqual(constants.TIMESTAMP_SPLIT_EPOCH, split_timestamp(0))

        # test timestamp
        self.assertDictEqual(constants.TIMESTAMP_SPLIT_TESTDATE,
            split_timestamp(1404913113))

    def test_split_isotimestamp(self):
        # test 0 timestamp (epoch)
        self.assertDictEqual(constants.TIMESTAMP_SPLIT_EPOCH,
            split_isotimestamp("1970-01-01T00:00:00"))

        # test timestamp
        self.assertDictEqual(constants.TIMESTAMP_SPLIT_TESTDATE,
            split_isotimestamp("2014-07-09T13:38:33"))

    def test_add_project_info_dict(self):
        # error is thrown when called without parameters
        self.assertRaises(TypeError, add_project_info_dict)

        # error is thrown when called with an invalid parameter
        self.assertRaises(TypeError, add_project_info_dict, None)
        self.assertRaises(TypeError, add_project_info_dict, "string")

        # add empty parameters
        self.assertDictEqual(
            {"buildtime_trend": self.project_info},
            add_project_info_dict({})
        )

        # set dict to add to
        self.assertDictEqual(
            {"test": "value", "buildtime_trend": self.project_info},
            add_project_info_dict({"test": "value"})
        )

    def test_add_project_info_list(self):
        # error is thrown when called without parameters
        self.assertRaises(TypeError, add_project_info_list)

        # error is thrown when called with an invalid parameter
        self.assertRaises(TypeError, add_project_info_list, None)

        # list should only have a dict as element
        self.assertRaises(TypeError, add_project_info_list, ["string"])

        # use empty list
        self.assertListEqual([], add_project_info_list([]))

        # use list with empty dict as single element
        self.assertListEqual(
            [{"buildtime_trend": self.project_info}],
            add_project_info_list([{}])
        )

        # list with one dict as element
        self.assertListEqual(
            [{"test": "value", "buildtime_trend": self.project_info}],
            add_project_info_list([{"test": "value"}])
        )

        # list with two dict as element
        self.assertListEqual(
            [{"test": "value", "buildtime_trend": self.project_info},
            {"test2": "value2", "buildtime_trend": self.project_info}],
            add_project_info_list([{"test": "value"},
                {"test2": "value2"}])
        )

    def test_check_file(self):
        # function should return false when file doesn't exist
        self.assertFalse(check_file('nofile.csv'))
        self.assertFalse(check_file(''))

        # function should throw an error when no filename is set
        self.assertRaises(TypeError, check_file)

        # function should return true if file exists
        self.assertTrue(check_file(constants.TEST_SAMPLE_FILE))

    def test_check_dict(self):
        # error is thrown when called without parameters
        self.assertRaises(TypeError, check_dict)

        # error is thrown when called with an invalid parameter
        with self.assertRaises(TypeError) as cm:
            check_dict(None, "name")
        self.assertEqual("param name should be a dictionary", str(cm.exception))

        with self.assertRaises(TypeError) as cm:
            check_dict("string", "string_name")
        self.assertEqual("param string_name should be a dictionary", str(cm.exception))

        # should return true if parameter is a dictionary
        self.assertTrue(check_dict({"string": "test"}, "name"))

        # should return true if key is found in dictionary
        self.assertTrue(check_dict({"string": "test"}, "string"))
        self.assertTrue(check_dict(
            {"string": "test", 7: "test"},
            list({7, "string"})
        ))

        # should return false if key is not found in dictionary
        self.assertTrue(check_dict({"string": "test"}, "name"))

    def test_keys_in_dict(self):
        # empty dict and empty key_list should return true
        self.assertTrue(keys_in_dict({}, []))
        self.assertTrue(keys_in_dict({"string": "test"}, []))

        # find 1 key in dict
        self.assertTrue(keys_in_dict({"string": "test"}, "string"))
        self.assertTrue(keys_in_dict({"string": "test", 7: "test"}, "string"))
        self.assertTrue(keys_in_dict({7: "test"}, 7))
        self.assertTrue(keys_in_dict({"string": "test", 7: "test"}, 7))

        # find multiple keys in dict
        self.assertTrue(keys_in_dict(
            {"string": "test", 7: "test"},
            list({7, "string"})
        ))

        # missing keys
        self.assertFalse(keys_in_dict({"string": "test"}, 7))
        self.assertFalse(keys_in_dict({7: "test"}, "string"))
        self.assertFalse(keys_in_dict({"string": "test"}, list({7, "string"})))

    def test_check_list(self):
        # error is thrown when called without parameters
        self.assertRaises(TypeError, check_list)

        # error is thrown when called with an invalid parameter
        with self.assertRaises(TypeError) as cm:
            check_list(None, "name")
        self.assertEqual("param name should be a list", str(cm.exception))

        with self.assertRaises(TypeError) as cm:
            check_list("string", "string_name")
        self.assertEqual("param string_name should be a list", str(cm.exception))

        # should return true if parameter is a list
        self.assertTrue(check_list(["string", "test"], "name"))
