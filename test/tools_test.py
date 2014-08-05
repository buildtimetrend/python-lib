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

from buildtimetrend.tools import format_timestamp
from buildtimetrend.tools import add_project_info_dict
from buildtimetrend.tools import add_project_info_list
from buildtimetrend.tools import get_project_info
import os
import unittest


class TestTools(unittest.TestCase):
    def setUp(self):
        project_name = "None"
        if 'TRAVIS' in os.environ and os.getenv('TRAVIS'):
            project_name = os.getenv('TRAVIS_REPO_SLUG')

        self.project_info = {"version": "0.1.1", "schema_version": "1",
            "project_name": project_name}

    def test_format_timestamp(self):
        # test 0 timestamp (epoch)
        self.assertEquals("1970-01-01T00:00:00", format_timestamp(0))

        # test timestamp
        self.assertEquals("2014-07-09T12:38:33", format_timestamp(1404909513))

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

    def test_get_project_info(self):
        self.assertDictEqual(self.project_info, get_project_info())
