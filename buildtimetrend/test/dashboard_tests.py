# vim: set expandtab sw=4 ts=4:
#
# Unit tests for Dashboard related functions
#
# Copyright (C) 2014-2016 Dieter Adriaenssens <ruleant@users.sourceforge.net>
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
from buildtimetrend.tools import check_file
import buildtimetrend.keenio
import os
import unittest
import mock
from buildtimetrend.test import constants


class TestDashboard(unittest.TestCase):

    """Unit tests for dashboard related functions"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixture."""
        cls.project_info = Settings().get_project_info()
        cls.maxDiff = None

    def tearDown(self):
        """Clean up after tests"""
        if (check_file(constants.DASHBOARD_TEST_CONFIG_FILE)):
            os.remove(constants.DASHBOARD_TEST_CONFIG_FILE)

    def test_get_config_dict(self):
        """Test get_config_dict()"""
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
        """Test get_config_string()"""
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

    @mock.patch(
        'buildtimetrend.dashboard.get_config_string',
        return_value="var config = {'projectName': 'test/repo3'};\n"
        "var keenConfig = {'projectId': '1234abcd'};"
    )
    def test_generate_config_file(self, get_cfg_str_func):
        """Test dashboard.generate_config_file()"""
        # set config file path
        Settings().add_setting(
            "dashboard_configfile",
            constants.DASHBOARD_TEST_CONFIG_FILE
        )

        # check if configfile exists
        self.assertFalse(check_file(constants.DASHBOARD_TEST_CONFIG_FILE))

        # generate config file with empty repo name
        self.assertRaises(TypeError, dashboard.generate_config_file)

        # generate config file with empty repo name
        self.assertTrue(dashboard.generate_config_file(None))

        self.assertTrue(check_file(constants.DASHBOARD_TEST_CONFIG_FILE))

        # check if mock was called with correct parameters
        args, kwargs = get_cfg_str_func.call_args
        self.assertEqual(args, (None, ))
        self.assertDictEqual(kwargs, {})

        # generate config file
        self.assertTrue(dashboard.generate_config_file("test/repo3"))

        self.assertTrue(check_file(constants.DASHBOARD_TEST_CONFIG_FILE))

        # check if mock was called with correct parameters
        args, kwargs = get_cfg_str_func.call_args
        self.assertEqual(args, ("test/repo3", ))
        self.assertDictEqual(kwargs, {})

        # test generated config file contents
        with open(constants.DASHBOARD_TEST_CONFIG_FILE, 'r') as config_file:
            self.assertEqual(
                "var config = {'projectName': 'test/repo3'};\n",
                next(config_file)
            )
            self.assertEqual(
                "var keenConfig = {'projectId': '1234abcd'};",
                next(config_file)
            )

    def test_generate_config_file_fails(self):
        """Test dashboard.generate_config_file() if creation fails"""
        # set config file path
        Settings().add_setting(
            "dashboard_configfile",
            constants.DASHBOARD_TEST_CONFIG_FILE
        )

        # check if configfile exists
        self.assertFalse(check_file(constants.DASHBOARD_TEST_CONFIG_FILE))

        # init mock
        patcher = mock.patch(
            'buildtimetrend.tools.check_file',
            return_value=False
        )
        check_file_func = patcher.start()

        # generation should return false
        self.assertFalse(dashboard.generate_config_file("test/repo4"))

        # check if mock was called with correct parameters
        args, kwargs = check_file_func.call_args
        self.assertEqual(
            args,
            (constants.DASHBOARD_TEST_CONFIG_FILE, )
        )
        self.assertDictEqual(kwargs, {})

        patcher.stop()

    def test_generate_config_file_ioerror(self):
        """
        Test dashboard.generate_config_file()
        if creation fails because of unexisting path.
        """
        # set config file path
        Settings().add_setting(
            "dashboard_configfile",
            "build/unexisting_path/config_test.js"
        )

        # generation should return false
        self.assertFalse(dashboard.generate_config_file("test/repo4"))
