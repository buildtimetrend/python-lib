# vim: set expandtab sw=4 ts=4:
#
# Unit tests for Dashboard related functions
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

from buildtimetrend import dashboard
from buildtimetrend.settings import Settings
from buildtimetrend.tools import is_string
import buildtimetrend.keenio
import os
import unittest
import mock
import constants


class TestDashboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.project_info = Settings().get_project_info()
        cls.maxDiff = None

    def test_get_config_dict(self):
        # error is thrown when extra parameter is not a dictionary
        self.assertRaises(
            TypeError,
            dashboard.get_config_dict, "test/repo", "should_be_dict"
        )

        # empty configuration
        self.assertDictEqual({}, dashboard.get_config_dict(""))

        # repo name is added
        self.assertDictEqual(
            {'projectName': 'test/repo', 'repoName': 'test/repo'},
            dashboard.get_config_dict("test/repo")
        )

        # add extra parameters
        self.assertEqual(
            {
                'projectName': 'test/repo', 'repoName': 'test/repo',
                'extra': 'value1', 'extra2': 'value2'
            },
            dashboard.get_config_dict(
                "test/repo", {'extra': 'value1', 'extra2': 'value2'}
            )
        )

    # decorators are applied from the bottom up see
    # https://docs.python.org/dev/library/unittest.mock.html#nesting-patch-decorators
    @mock.patch(
        'buildtimetrend.keenio.get_dashboard_keen_config',
        return_value={'projectId': '1234abcd'}
    )
    @mock.patch(
        'buildtimetrend.dashboard.get_config_dict',
        return_value={'projectName': 'test/repo'}
    )
    def test_get_config_string(
            self, config_dict_func, keen_config_func
    ):
        self.assertEqual(
            "var config = {'projectName': 'test/repo'};"
            "\nvar keenConfig = {'projectId': '1234abcd'};",
            dashboard.get_config_string("test/repo")
        )

        # function was last called with argument "test/repo"
        args, kwargs = keen_config_func.call_args
        self.assertEqual(args, ("test/repo",))
        self.assertDictEqual(kwargs, {})

        args, kwargs = config_dict_func.call_args
        self.assertEqual(args, ("test/repo", None))
        self.assertDictEqual(kwargs, {})

        # call function with argument "test/repo2"
        # and a dict with extra parameters
        dashboard.get_config_string("test/repo2", {'extra': 'value'})
        args, kwargs = keen_config_func.call_args
        self.assertEqual(args, ("test/repo2",))
        self.assertDictEqual(kwargs, {})

        args, kwargs = config_dict_func.call_args
        self.assertEqual(args, ("test/repo2", {'extra': 'value'}))
        self.assertDictEqual(kwargs, {})
