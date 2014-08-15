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
from buildtimetrend.tools import split_isotimestamp
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

        self.project_info = {"version": "0.2-dev", "schema_version": "1",
            "project_name": project_name}

    def test_format_timestamp(self):
        # test 0 timestamp (epoch)
        self.assertEquals("1970-01-01T00:00:00", format_timestamp(0))

        # test timestamp
        self.assertEquals("2014-07-09T12:38:33", format_timestamp(1404909513))

    def test_split_isotimestamp(self):
        # test 0 timestamp (epoch)
        self.assertDictEqual(
            {
                "timestamp": "1970-01-01T00:00:00",
                "year": "1970",
                "month": "01",
                "month_short_en": "Jan",
                "month_full_en": "January",
                "day_of_month": "01",
                "day_of_week": "4",
                "day_of_week_short_en": "Thu",
                "day_of_week_full_en": "Thursday",
                "hour_12": "12",
                "hour_ampm": "AM",
                "hour_24": "00",
                "minute": "00",
                "second": "00",
            },
            split_isotimestamp("1970-01-01T00:00:00")
        )

        # test timestamp
        self.assertDictEqual(
             {
                "timestamp": "2014-07-09T13:38:33",
                "year": "2014",
                "month": "07",
                "month_short_en": "Jul",
                "month_full_en": "July",
                "day_of_month": "09",
                "day_of_week": "3",
                "day_of_week_short_en": "Wed",
                "day_of_week_full_en": "Wednesday",
                "hour_12": "01",
                "hour_ampm": "PM",
                "hour_24": "13",
                "minute": "38",
                "second": "33",
           },
           split_isotimestamp("2014-07-09T13:38:33")
        )

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
