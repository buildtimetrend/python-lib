# vim: set expandtab sw=4 ts=4:
#
# Unit tests for Keen functions
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

from buildtimetrend.keenio import *
from buildtimetrend.settings import Settings
import os
import keen
import unittest
import constants
import logging

class TestTools(unittest.TestCase):
    copy_keen_project_id = None
    copy_keen_write_key = None
    copy_keen_read_key = None

    @classmethod
    def setUpClass(self):
        self.project_info = Settings().get_project_info()
        self.maxDiff = None

        # copy Keen.io environment variables
        if "KEEN_PROJECT_ID" in os.environ:
            self.copy_keen_project_id = os.environ["KEEN_PROJECT_ID"]
        if "KEEN_WRITE_KEY" in os.environ:
            self.copy_keen_write_key = os.environ["KEEN_WRITE_KEY"]
        if "KEEN_READ_KEY" in os.environ:
            self.copy_keen_read_key = os.environ["KEEN_READ_KEY"]

    @classmethod
    def tearDownClass(self):
        # restore saved Keen.io environment variables
        if self.copy_keen_project_id is not None:
            os.environ["KEEN_PROJECT_ID"] = self.copy_keen_project_id
        if self.copy_keen_write_key is not None:
            os.environ["KEEN_WRITE_KEY"] = self.copy_keen_write_key
        if self.copy_keen_read_key is not None:
            os.environ["KEEN_READ_KEY"] = self.copy_keen_read_key

    def setUp(self):
        # reset Keen.io environment variables before each test
        if "KEEN_PROJECT_ID" in os.environ:
            del os.environ["KEEN_PROJECT_ID"]
        if "KEEN_WRITE_KEY" in os.environ:
            del os.environ["KEEN_WRITE_KEY"]
        if "KEEN_READ_KEY" in os.environ:
            del os.environ["KEEN_READ_KEY"]

        # reset Keen.io connection settings before each test
        keen.project_id = None
        keen.write_key = None
        keen.read_key = None

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

         # dict with finished_at timestamp
        self.assertDictEqual(
                {"test": "value",
                "buildtime_trend": self.project_info,
                "build": {"finished_at": constants.SPLIT_TIMESTAMP_FINISHED},
                "keen": {"timestamp": constants.ISOTIMESTAMP_FINISHED}
            },
            add_project_info_dict(
                {"test": "value",
                "build": {"finished_at": constants.SPLIT_TIMESTAMP_FINISHED}
            })
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

    def test_keen_io_writable_keen_var(self):
        self.assertEqual(None, keen.project_id)
        self.assertEqual(None, keen.write_key)

        self.assertFalse(keen_io_writable())

        keen.project_id = "1234abcd"
        keen.write_key = "1234abcd5678efgh"

        self.assertTrue(keen_io_writable())

    def test_keen_io_writable_envir_vars(self):
        self.assertFalse(keen_io_writable())

        os.environ["KEEN_PROJECT_ID"] = "1234abcd"
        os.environ["KEEN_WRITE_KEY"] = "1234abcd5678efgh"

        self.assertTrue(keen_io_writable())
