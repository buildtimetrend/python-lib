# vim: set expandtab sw=4 ts=4:
#
# Unit tests for Keen functions
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

from buildtimetrend import keenio
from buildtimetrend.keenio import keen_io_generate_read_key
from buildtimetrend.keenio import keen_io_generate_write_key
from buildtimetrend.keenio import get_all_projects
from buildtimetrend.keenio import get_avg_buildtime
from buildtimetrend.keenio import get_dashboard_keen_config
from buildtimetrend.keenio import get_latest_buildtime
from buildtimetrend.keenio import get_passed_build_jobs
from buildtimetrend.keenio import get_repo_filter
from buildtimetrend.keenio import get_total_build_jobs
from buildtimetrend.keenio import get_total_builds
from buildtimetrend.keenio import get_pct_passed_build_jobs
from buildtimetrend.settings import Settings
from buildtimetrend.tools import is_string
from buildtimetrend.buildjob import BuildJob
import os
import keen
import requests
import copy
import unittest
import mock
from buildtimetrend.test import constants


class TestKeen(unittest.TestCase):

    """Unit tests for Keen related functions"""

    copy_keen_project_id = None
    copy_keen_write_key = None
    copy_keen_read_key = None
    copy_keen_master_key = None

    @classmethod
    def setUpClass(cls):
        """Set up test fixture."""
        cls.settings = Settings()
        cls.project_info = cls.settings.get_project_info()
        cls.maxDiff = None

        # copy Keen.io environment variables
        if "KEEN_PROJECT_ID" in os.environ:
            cls.copy_keen_project_id = os.environ["KEEN_PROJECT_ID"]
        if "KEEN_WRITE_KEY" in os.environ:
            cls.copy_keen_write_key = os.environ["KEEN_WRITE_KEY"]
        if "KEEN_READ_KEY" in os.environ:
            cls.copy_keen_read_key = os.environ["KEEN_READ_KEY"]
        if "KEEN_MASTER_KEY" in os.environ:
            cls.copy_keen_master_key = os.environ["KEEN_MASTER_KEY"]

    @classmethod
    def tearDownClass(cls):
        """Restore to state before test environment."""
        # restore saved Keen.io environment variables
        if cls.copy_keen_project_id is not None:
            os.environ["KEEN_PROJECT_ID"] = cls.copy_keen_project_id
        if cls.copy_keen_write_key is not None:
            os.environ["KEEN_WRITE_KEY"] = cls.copy_keen_write_key
        if cls.copy_keen_read_key is not None:
            os.environ["KEEN_READ_KEY"] = cls.copy_keen_read_key
        if cls.copy_keen_master_key is not None:
            os.environ["KEEN_MASTER_KEY"] = cls.copy_keen_master_key

    def setUp(self):
        """Initialise test environment before each test."""
        # reinit settings singleton
        if self.settings is not None:
            self.settings.__init__()

        # reset Keen.io environment variables before each test
        if "KEEN_PROJECT_ID" in os.environ:
            del os.environ["KEEN_PROJECT_ID"]
        if "KEEN_WRITE_KEY" in os.environ:
            del os.environ["KEEN_WRITE_KEY"]
        if "KEEN_READ_KEY" in os.environ:
            del os.environ["KEEN_READ_KEY"]
        if "KEEN_MASTER_KEY" in os.environ:
            del os.environ["KEEN_MASTER_KEY"]

        # reset Keen.io connection settings before each test
        keen._client = None
        keen.project_id = None
        keen.write_key = None
        keen.read_key = None
        keen.master_key = None

    def raise_conn_err(*args, **kwargs):
        """Mock function raising a Connection Error"""
        raise requests.ConnectionError

    def test_novalues(self):
        """Test initial state the function and classs instances."""
        self.assertEqual(None, keen.project_id)
        self.assertEqual(None, keen.write_key)
        self.assertEqual(None, keen.read_key)
        self.assertEqual(None, keen.master_key)

        self.assertFalse(keenio.keen_has_project_id())
        self.assertFalse(keenio.keen_has_master_key())
        self.assertFalse(keenio.keen_has_write_key())
        self.assertFalse(keenio.keen_has_read_key())
        self.assertFalse(keenio.keen_is_writable())
        self.assertFalse(keenio.keen_is_readable())

    def test_add_project_info_dict(self):
        """Test keenio.add_project_info_dict()"""
        # error is thrown when called without parameters
        self.assertRaises(TypeError, keenio.add_project_info_dict)

        # error is thrown when called with an invalid parameter
        self.assertRaises(TypeError, keenio.add_project_info_dict, None)
        self.assertRaises(TypeError, keenio.add_project_info_dict, "string")

        # add empty parameters
        self.assertDictEqual(
            {"buildtime_trend": self.project_info},
            keenio.add_project_info_dict({})
        )

        # set dict to add to
        self.assertDictEqual(
            {"test": "value", "buildtime_trend": self.project_info},
            keenio.add_project_info_dict({"test": "value"})
        )

        # job.repo overrides buildtime_trend.project_name
        TEST_NAME = "test/name"
        tmp_project_info = copy.deepcopy(self.project_info)
        tmp_project_info["project_name"] = TEST_NAME
        self.assertDictEqual(
            {
                "test": "value",
                "buildtime_trend": tmp_project_info,
                "job": {"repo": TEST_NAME},
            },
            keenio.add_project_info_dict({
                "test": "value",
                "job": {"repo": TEST_NAME}
            })
        )

        # dict with finished_at timestamp
        self.assertDictEqual(
            {
                "test": "value",
                "buildtime_trend": self.project_info,
                "job": {"finished_at": constants.SPLIT_TIMESTAMP_FINISHED},
                "keen": {"timestamp": constants.ISOTIMESTAMP_FINISHED}
            },
            keenio.add_project_info_dict({
                "test": "value",
                "job": {"finished_at": constants.SPLIT_TIMESTAMP_FINISHED}
            })
        )

    def test_add_project_info_list(self):
        """Test keenio.add_project_info_list()"""
        # error is thrown when called without parameters
        self.assertRaises(TypeError, keenio.add_project_info_list)

        # error is thrown when called with an invalid parameter
        self.assertRaises(TypeError, keenio.add_project_info_list, None)

        # list should only have a dict as element
        self.assertRaises(TypeError, keenio.add_project_info_list, ["string"])

        # use empty list
        self.assertListEqual([], keenio.add_project_info_list([]))

        # use list with empty dict as single element
        self.assertListEqual(
            [{"buildtime_trend": self.project_info}],
            keenio.add_project_info_list([{}])
        )

        # list with one dict as element
        self.assertListEqual(
            [{"test": "value", "buildtime_trend": self.project_info}],
            keenio.add_project_info_list([{"test": "value"}])
        )

        # list with two dict as element
        self.assertListEqual([
            {"test": "value", "buildtime_trend": self.project_info},
            {"test2": "value2", "buildtime_trend": self.project_info}],
            keenio.add_project_info_list([
                {"test": "value"},
                {"test2": "value2"}])
        )

    def test_keen_has_project_id_keen_var(self):
        """Test keenio.keen_has_project_id() with keen vars"""
        keen.project_id = "1234abcd"

        self.assertTrue(keenio.keen_has_project_id())

    def test_keen_has_project_id_env_var(self):
        """Test keenio.keen_has_project_id() with env vars"""
        os.environ["KEEN_PROJECT_ID"] = "1234abcd"
        keen.project_id = "1234abcd"

        self.assertTrue(keenio.keen_has_project_id())

    def test_keen_has_master_key_keen_var(self):
        """Test keenio.keen_has_master_key() with keen vars"""
        keen.master_key = "abcd1234"
        keen.project_id = "1234abcd"

        self.assertTrue(keenio.keen_has_master_key())

    def test_keen_has_master_key_env_vars(self):
        """Test keenio.keen_has_master_key() with env vars"""
        os.environ["KEEN_MASTER_KEY"] = "abcd1234"

        self.assertTrue(keenio.keen_has_master_key())

    def test_keen_is_writable_keen_var(self):
        """Test keenio.keen_is_writable() with keen vars"""
        # only set project id, check should fail
        keen.project_id = "1234abcd"

        self.assertFalse(keenio.keen_is_writable())

        # set write_key
        keen.write_key = "1234abcd5678efgh"

        self.assertTrue(keenio.keen_is_writable())

    def test_keen_is_writable_env_vars(self):
        """Test keenio.keen_is_writable() with env vars"""
        # only set project id, check should fail
        os.environ["KEEN_PROJECT_ID"] = "1234abcd"
        self.assertFalse(keenio.keen_is_writable())

        # set write_key
        os.environ["KEEN_WRITE_KEY"] = "1234abcd5678efgh"
        self.assertTrue(keenio.keen_is_writable())

    def test_keen_has_write_key_keen_var(self):
        """Test keenio.keen_has_write_key() with keen vars"""
        # set write_key
        keen.write_key = "4567abcd5678efgh"
        self.assertTrue(keenio.keen_has_write_key())

    def test_keen_has_write_key_env_vars(self):
        """Test keenio.keen_has_write_key() with env vars"""
        # set write_key
        os.environ["KEEN_WRITE_KEY"] = "4567abcd5678efgh"
        self.assertTrue(keenio.keen_has_write_key())

    def test_keen_has_read_key_keen_var(self):
        """Test keenio.keen_has_read_key() with keen vars"""
        # set read_key
        keen.read_key = "4567abcd5678efgh"
        self.assertTrue(keenio.keen_has_read_key())

    def test_keen_has_read_key_env_vars(self):
        """Test keenio.keen_has_read_key() with env vars"""
        # set read_key
        os.environ["KEEN_READ_KEY"] = "4567abcd5678efgh"
        self.assertTrue(keenio.keen_has_read_key())

    def test_keen_is_readable_keen_var(self):
        """Test keenio.keen_is_readable() with keen vars"""
        # only set project id, check should fail
        keen.project_id = "1234abcd"
        self.assertFalse(keenio.keen_is_readable())

        # set read_key
        keen.read_key = "4567abcd5678efgh"
        self.assertTrue(keenio.keen_is_readable())

    def test_keen_is_readable_env_vars(self):
        """Test keenio.keen_is_readable() with env vars"""
        # only set project id, check should fail
        os.environ["KEEN_PROJECT_ID"] = "1234abcd"
        self.assertFalse(keenio.keen_is_readable())

        # set read_key
        os.environ["KEEN_READ_KEY"] = "4567abcd5678efgh"
        self.assertTrue(keenio.keen_is_readable())

    def test_generate_read_key(self):
        """Test keenio.generate_read_key()"""
        # should return None if master key is not set
        self.assertEqual(None, keen_io_generate_read_key(None))
        self.assertEqual(None, keen_io_generate_read_key("test/project"))

        # set master_key
        os.environ["KEEN_MASTER_KEY"] = "4567abcd5678efgh"
        self.assertTrue(isinstance(keen_io_generate_read_key(None), bytes))
        self.assertTrue(
            isinstance(keen_io_generate_read_key("test/project"), bytes)
        )

    def test_generate_write_key(self):
        """Test keenio.generate_write_key()"""
        # should return None if master key is not set
        self.assertEqual(None, keen_io_generate_write_key())

        # set master_key
        os.environ["KEEN_MASTER_KEY"] = "4567abcd5678efgh"
        self.assertTrue(isinstance(keen_io_generate_write_key(), bytes))

    def test_get_repo_filter(self):
        """Test keenio.get_repo_filter()"""
        self.assertEqual(None, get_repo_filter())
        self.assertEqual(None, get_repo_filter(None))

        self.assertDictEqual({
            "property_name": "buildtime_trend.project_name",
            "operator": "eq",
            "property_value": "repo/name"},
            get_repo_filter("repo/name")
        )

        self.assertDictEqual({
            "property_name": "buildtime_trend.project_name",
            "operator": "eq",
            "property_value": "1234"},
            get_repo_filter(1234)
        )

    def test_check_time_interval(self):
        """Test keenio.check_time_interval()"""
        # empty or undefined defaults to 'week'
        self.assertDictEqual(
            {'name': 'week', 'timeframe': 'this_7_days', 'max_age': 600},
            keenio.check_time_interval()
        )
        self.assertDictEqual(
            {'name': 'week', 'timeframe': 'this_7_days', 'max_age': 600},
            keenio.check_time_interval(None)
        )
        self.assertDictEqual(
            {'name': 'week', 'timeframe': 'this_7_days', 'max_age': 600},
            keenio.check_time_interval(1234)
        )
        self.assertDictEqual(
            {'name': 'week', 'timeframe': 'this_7_days', 'max_age': 600},
            keenio.check_time_interval([])
        )

        # valid entries : week, month, year
        self.assertDictEqual(
            {'name': 'week', 'timeframe': 'this_7_days', 'max_age': 600},
            keenio.check_time_interval("week")
        )
        self.assertDictEqual(
            {'name': 'month', 'timeframe': 'this_30_days', 'max_age': 600},
            keenio.check_time_interval("month")
        )
        self.assertDictEqual(
            {'name': 'year', 'timeframe': 'this_52_weeks', 'max_age': 1800},
            keenio.check_time_interval("year")
        )

        # valid entries are case insensitive
        self.assertDictEqual(
            {'name': 'week', 'timeframe': 'this_7_days', 'max_age': 600},
            keenio.check_time_interval("wEEk")
        )
        self.assertDictEqual(
            {'name': 'month', 'timeframe': 'this_30_days', 'max_age': 600},
            keenio.check_time_interval("moNth")
        )

    def test_get_result_color(self):
        """Test keenio.get_result_color()"""
        self.assertEqual("red", keenio.get_result_color())
        self.assertEqual("lightgrey", keenio.get_result_color(None))
        self.assertEqual("lightgrey", keenio.get_result_color(None, None))
        self.assertEqual(
            "lightgrey", keenio.get_result_color(None, None, None)
        )
        self.assertEqual("lightgrey", keenio.get_result_color(None))
        self.assertEqual("lightgrey", keenio.get_result_color(123, None))
        self.assertEqual("lightgrey", keenio.get_result_color(123, 34, None))
        self.assertEqual("lightgrey", keenio.get_result_color("string"))
        self.assertEqual("lightgrey", keenio.get_result_color(123, "string"))
        self.assertEqual(
            "lightgrey", keenio.get_result_color(123, 34, "string")
        )

        # test 'OK' threshold
        self.assertEqual("green", keenio.get_result_color(100))
        self.assertEqual("green", keenio.get_result_color(100.0))
        self.assertEqual("green", keenio.get_result_color(91))
        self.assertEqual("green", keenio.get_result_color(90))
        self.assertEqual("green", keenio.get_result_color(90.0))

        # test 'warning' threshold
        self.assertEqual("yellow", keenio.get_result_color(89))
        self.assertEqual("yellow", keenio.get_result_color(89.9))
        self.assertEqual("yellow", keenio.get_result_color(71))
        self.assertEqual("yellow", keenio.get_result_color(70))
        self.assertEqual("yellow", keenio.get_result_color(70.0))

        # test 'error' threshold
        self.assertEqual("red", keenio.get_result_color(69))
        self.assertEqual("red", keenio.get_result_color(69.9))
        self.assertEqual("red", keenio.get_result_color(50))
        self.assertEqual("red", keenio.get_result_color(50.0))
        self.assertEqual("red", keenio.get_result_color(0))
        self.assertEqual("red", keenio.get_result_color(-10))

        # test custom thresholds
        self.assertEqual("green", keenio.get_result_color(100, 75, 50))
        self.assertEqual("green", keenio.get_result_color(76, 75, 50))
        self.assertEqual("green", keenio.get_result_color(75, 75, 50))
        self.assertEqual("yellow", keenio.get_result_color(74, 75, 50))
        self.assertEqual("yellow", keenio.get_result_color(51, 75, 50))
        self.assertEqual("yellow", keenio.get_result_color(50, 75, 50))
        self.assertEqual("red", keenio.get_result_color(49, 75, 50))
        self.assertEqual("red", keenio.get_result_color(0, 75, 50))
        self.assertEqual("red", keenio.get_result_color(-10, 75, 50))

    def test_has_build_id(self):
        """Test keenio.has_build_id()"""
        # error is thrown when called without parameters
        self.assertRaises(ValueError, keenio.has_build_id)

        # error is thrown when called with an invalid parameter
        self.assertRaises(ValueError, keenio.has_build_id, None, None)

        # error is thrown when project_id or read key is not set
        self.assertRaises(SystemError, keenio.has_build_id, "test", 123)

        # test with an invalid token
        keen.project_id = "1234abcd"
        keen.read_key = "4567abcd5678efgh"
        self.assertRaises(SystemError, keenio.has_build_id, "test", 123)

    @mock.patch('keen.count', return_value=0)
    def test_has_build_id_mock(self, keen_count_func):
        """Test keenio.has_build_id() with a mocked keen.count"""
        # test with some token (value doesn't matter, keen.count is mocked)
        keen.project_id = "1234abcd"
        keen.read_key = "4567abcd5678efgh"
        # should return false if ID doesn't exist
        self.assertFalse(keenio.has_build_id("test", 123))

        # should return true if does exist
        keen_count_func.return_value = 1
        self.assertTrue(keenio.has_build_id("test", 123))

        # test raising ConnectionError
        keen_count_func.side_effect = self.raise_conn_err
        self.assertRaises(SystemError, keenio.has_build_id, "test", 123)

    @mock.patch(
        'buildtimetrend.keenio.keen_io_generate_read_key',
        return_value=None
    )
    def test_get_dashboard_keen_config(self, gen_key_func):
        """Test keenio.get_dashboard_keen_config()"""
        self.assertDictEqual({}, get_dashboard_keen_config("test"))

        # test with a project id
        keen.master_key = '4567abcd5678efgh'
        self.assertDictEqual({}, get_dashboard_keen_config("test"))

        # test with a KEEN_PROJECT_ID
        os.environ["KEEN_PROJECT_ID"] = 'abcd1234'
        self.assertDictEqual(
            {'projectId': 'abcd1234'}, get_dashboard_keen_config("test")
        )

        # test with a keen.project_id
        keen.project_id = '1234abcd'
        self.assertDictEqual(
            {'projectId': '1234abcd'}, get_dashboard_keen_config("test")
        )

        # test with a generated read_key
        gen_key_func.return_value = 'fedcba9876543210abcdefg'
        self.assertDictEqual(
            {
                'projectId': '1234abcd',
                'readKey': 'fedcba9876543210abcdefg'
            },
            get_dashboard_keen_config("test")
        )

        # test with a generated read_key (bytes)
        gen_key_func.return_value = b'fedcba9876543210abcdefg'
        self.assertDictEqual(
            {
                'projectId': '1234abcd',
                'readKey': 'fedcba9876543210abcdefg'
            },
            get_dashboard_keen_config("test")
        )

    def test_get_avg_buildtime(self):
        """Test keenio.get_avg_buildtime()"""
        patcher = mock.patch('keen.average', return_value=123)
        keen_avg_func = patcher.start()

        self.assertEqual(-1, get_avg_buildtime())
        self.assertEqual(-1, get_avg_buildtime("test/repo"))

        # test with some token (value doesn't matter, keen.average is mocked)
        keen.project_id = "1234abcd"
        keen.read_key = "4567abcd5678efgh"
        self.assertEqual(123, get_avg_buildtime("test/repo"))

        # test parameters passed to keen.average
        args, kwargs = keen_avg_func.call_args
        self.assertEqual(args, ("build_jobs",))
        self.assertDictEqual(kwargs, {
            'target_property': 'job.duration',
            'timeframe': keenio.TIME_INTERVALS['week']['timeframe'],
            'max_age': keenio.TIME_INTERVALS['week']['max_age'],
            'filters': [{
                'operator': 'eq',
                'property_name': 'buildtime_trend.project_name',
                'property_value': 'test/repo'
            }]
        })

        self.assertEqual(123, get_avg_buildtime("test/repo2", "year"))

        # test parameters passed to keen.average
        args, kwargs = keen_avg_func.call_args
        self.assertEqual(args, ("build_jobs",))
        self.assertDictEqual(kwargs, {
            'target_property': 'job.duration',
            'timeframe': keenio.TIME_INTERVALS['year']['timeframe'],
            'max_age': keenio.TIME_INTERVALS['year']['max_age'],
            'filters': [{
                'operator': 'eq',
                'property_name': 'buildtime_trend.project_name',
                'property_value': 'test/repo2'
            }]
        })

        # test raising ConnectionError
        keen_avg_func.side_effect = self.raise_conn_err
        self.assertEqual(-1, get_avg_buildtime("test/repo"))

        # test raising KeenApiError (call with invalid read_key)
        patcher.stop()
        self.assertEqual(-1, get_avg_buildtime("test/repo"))

    def test_get_total_build_jobs(self):
        """Test keenio.get_total_build_jobs()"""
        patcher = mock.patch('keen.count_unique', return_value=234)
        keen_count_func = patcher.start()

        self.assertEqual(-1, get_total_build_jobs())
        self.assertEqual(-1, get_total_build_jobs("test/repo"))

        # test with some token (value doesn't matter, keen.average is mocked)
        keen.project_id = "1234abcd"
        keen.read_key = "4567abcd5678efgh"
        self.assertEqual(234, get_total_build_jobs("test/repo"))

        # test parameters passed to keen.average
        args, kwargs = keen_count_func.call_args
        self.assertEqual(args, ("build_jobs",))
        self.assertDictEqual(kwargs, {
            'target_property': 'job.job',
            'timeframe': keenio.TIME_INTERVALS['week']['timeframe'],
            'max_age': keenio.TIME_INTERVALS['week']['max_age'],
            'filters': [{
                'operator': 'eq',
                'property_name': 'buildtime_trend.project_name',
                'property_value': 'test/repo'
            }]
        })

        self.assertEqual(234, get_total_build_jobs("test/repo2", "year"))

        # test parameters passed to keen.average
        args, kwargs = keen_count_func.call_args
        self.assertEqual(args, ("build_jobs",))
        self.assertDictEqual(kwargs, {
            'target_property': 'job.job',
            'timeframe': keenio.TIME_INTERVALS['year']['timeframe'],
            'max_age': keenio.TIME_INTERVALS['year']['max_age'],
            'filters': [{
                'operator': 'eq',
                'property_name': 'buildtime_trend.project_name',
                'property_value': 'test/repo2'
            }]
        })

        # test raising ConnectionError
        keen_count_func.side_effect = self.raise_conn_err
        self.assertEqual(-1, get_total_build_jobs("test/repo"))

        # test raising KeenApiError (call with invalid read_key)
        patcher.stop()
        self.assertEqual(-1, get_total_build_jobs("test/repo"))

    def test_get_passed_build_jobs(self):
        """Test keenio.get_passed_build_jobs()"""
        patcher = mock.patch('keen.count_unique', return_value=34)
        keen_count_func = patcher.start()

        self.assertEqual(-1, get_passed_build_jobs())
        self.assertEqual(-1, get_passed_build_jobs("test/repo"))

        # test with some token (value doesn't matter, keen.average is mocked)
        keen.project_id = "1234abcd"
        keen.read_key = "4567abcd5678efgh"
        self.assertEqual(34, get_passed_build_jobs("test/repo"))

        # test parameters passed to keen.average
        args, kwargs = keen_count_func.call_args
        self.assertEqual(args, ("build_jobs",))
        self.assertDictEqual(kwargs, {
            'target_property': 'job.job',
            'timeframe': keenio.TIME_INTERVALS['week']['timeframe'],
            'max_age': keenio.TIME_INTERVALS['week']['max_age'],
            'filters': [
                {
                    'operator': 'eq',
                    'property_name': 'buildtime_trend.project_name',
                    'property_value': 'test/repo'
                },
                {
                    "property_name": "job.result",
                    "operator": "eq",
                    "property_value": "passed"
                }
            ]
        })

        self.assertEqual(34, get_passed_build_jobs("test/repo2", "year"))

        # test parameters passed to keen.average
        args, kwargs = keen_count_func.call_args
        self.assertEqual(args, ("build_jobs",))
        self.assertDictEqual(kwargs, {
            'target_property': 'job.job',
            'timeframe': keenio.TIME_INTERVALS['year']['timeframe'],
            'max_age': keenio.TIME_INTERVALS['year']['max_age'],
            'filters': [
                {
                    'operator': 'eq',
                    'property_name': 'buildtime_trend.project_name',
                    'property_value': 'test/repo2'
                },
                {
                    "property_name": "job.result",
                    "operator": "eq",
                    "property_value": "passed"
                }
            ]
        })

        # test raising ConnectionError
        keen_count_func.side_effect = self.raise_conn_err
        self.assertEqual(-1, get_passed_build_jobs("test/repo"))

        # test raising KeenApiError (call with invalid read_key)
        patcher.stop()
        self.assertEqual(-1, get_passed_build_jobs("test/repo"))

    def test_get_total_builds(self):
        """Test keenio.get_total_builds()"""
        patcher = mock.patch('keen.count_unique', return_value=345)
        keen_count_func = patcher.start()

        self.assertEqual(-1, get_total_builds())
        self.assertEqual(-1, get_total_builds("test/repo"))

        # test with some token (value doesn't matter, keen.average is mocked)
        keen.project_id = "1234abcd"
        keen.read_key = "4567abcd5678efgh"
        self.assertEqual(345, get_total_builds("test/repo"))

        # test parameters passed to keen.average
        args, kwargs = keen_count_func.call_args
        self.assertEqual(args, ("build_jobs",))
        self.assertDictEqual(kwargs, {
            'target_property': 'job.build',
            'timeframe': keenio.TIME_INTERVALS['week']['timeframe'],
            'max_age': keenio.TIME_INTERVALS['week']['max_age'],
            'filters': [{
                'operator': 'eq',
                'property_name': 'buildtime_trend.project_name',
                'property_value': 'test/repo'
            }]
        })

        self.assertEqual(345, get_total_builds("test/repo2", "year"))

        # test parameters passed to keen.average
        args, kwargs = keen_count_func.call_args
        self.assertEqual(args, ("build_jobs",))
        self.assertDictEqual(kwargs, {
            'target_property': 'job.build',
            'timeframe': keenio.TIME_INTERVALS['year']['timeframe'],
            'max_age': keenio.TIME_INTERVALS['year']['max_age'],
            'filters': [{
                'operator': 'eq',
                'property_name': 'buildtime_trend.project_name',
                'property_value': 'test/repo2'
            }]
        })

        # test raising ConnectionError
        keen_count_func.side_effect = self.raise_conn_err
        self.assertEqual(-1, get_total_builds("test/repo"))

        # test raising KeenApiError (call with invalid read_key)
        patcher.stop()
        self.assertEqual(-1, get_total_builds("test/repo"))

    def test_get_latest_buildtime(self):
        """Test keenio.get_latest_buildtime()"""
        patcher = mock.patch(
            'keen.extraction',
            return_value=[
                {
                    "job": {
                        "duration": 345.56
                    }
                }
            ]
        )
        keen_extract_func = patcher.start()

        self.assertEqual(-1, get_latest_buildtime())
        self.assertEqual(-1, get_latest_buildtime("test/repo"))

        # test with some token (value doesn't matter, keen.extract is mocked)
        keen.project_id = "1234abcd"
        keen.read_key = "4567abcd5678efgh"
        self.assertEqual(345.56, get_latest_buildtime("test/repo"))

        # test parameters passed to keen.average
        args, kwargs = keen_extract_func.call_args
        self.assertEqual(args, ("build_jobs",))
        self.assertDictEqual(kwargs, {
            'property_names': 'job.duration',
            'latest': 1,
            'filters': [{
                'operator': 'eq',
                'property_name': 'buildtime_trend.project_name',
                'property_value': 'test/repo'
            }]
        })

        # query returned two values (shouldn't happen, but test anyway)
        keen_extract_func.return_value = [
            {
                "job": {
                    "duration": 123.45
                }
            },
            {
                "job": {
                    "duration": 345.56
                }
            }
        ]
        self.assertEqual(123.45, get_latest_buildtime("test/repo"))

        # return -1 if no value is returned
        keen_extract_func.return_value = []
        self.assertEqual(-1, get_latest_buildtime("test/repo"))

        # returned value is invalid
        keen_extract_func.return_value = [
            {
                "something": {
                    "else": 345.56
                }
            }
        ]
        self.assertEqual(-1, get_latest_buildtime("test/repo"))

        # returned value is empty
        keen_extract_func.return_value = None
        self.assertEqual(-1, get_latest_buildtime("test/repo"))

        # returned value isn't a list
        keen_extract_func.return_value = {}
        self.assertEqual(-1, get_latest_buildtime("test/repo"))
        keen_extract_func.return_value = 1234
        self.assertEqual(-1, get_latest_buildtime("test/repo"))
        keen_extract_func.return_value = "test"
        self.assertEqual(-1, get_latest_buildtime("test/repo"))

        # test raising ConnectionError
        keen_extract_func.side_effect = self.raise_conn_err
        self.assertEqual(-1, get_latest_buildtime("test/repo"))

        # test raising KeenApiError (call with invalid read_key)
        patcher.stop()
        self.assertEqual(-1, get_latest_buildtime("test/repo"))

    def test_get_all_projects(self):
        """Test keenio.get_all_projects()"""
        patcher = mock.patch(
            'keen.select_unique',
            return_value=["project1", "project2"]
        )
        keen_select_func = patcher.start()

        self.assertListEqual([], get_all_projects())

        # test with some token (value doesn't matter, keen.extract is mocked)
        keen.project_id = "1234abcd"
        keen.read_key = "4567abcd5678efgh"
        self.assertListEqual(["project1", "project2"], get_all_projects())

        # test parameters passed to keen.average
        args, kwargs = keen_select_func.call_args
        self.assertEqual(args, ("build_jobs", "buildtime_trend.project_name"))
        self.assertDictEqual(kwargs, {'max_age': 86400})

        # returned value is invalid
        keen_select_func.return_value = "invalid"
        self.assertListEqual([], get_all_projects())

        # returned value is empty
        keen_select_func.return_value = None
        self.assertListEqual([], get_all_projects())
        keen_select_func.return_value = []
        self.assertListEqual([], get_all_projects())

        # returned value isn't a list
        keen_select_func.return_value = {}
        self.assertListEqual([], get_all_projects())
        keen_select_func.return_value = 1234
        self.assertListEqual([], get_all_projects())
        keen_select_func.return_value = "test"
        self.assertListEqual([], get_all_projects())

        # test raising ConnectionError
        keen_select_func.side_effect = self.raise_conn_err
        self.assertListEqual([], get_all_projects())

        # test raising KeenApiError (call with invalid read_key)
        patcher.stop()
        self.assertListEqual([], get_all_projects())

    # decorators are applied from the bottom up see
    # https://docs.python.org/dev/library/unittest.mock.html#nesting-patch-decorators
    @mock.patch(
        'buildtimetrend.keenio.get_total_build_jobs', return_value=100
    )
    @mock.patch(
        'buildtimetrend.keenio.get_passed_build_jobs', return_value=75
    )
    def test_pct_passed_build_jobs(self, passed_func, total_func):
        """Test keenio.get_pct_passed_build_jobs()"""
        self.assertEqual(75, get_pct_passed_build_jobs("test/repo", "week"))

        # function was last called with argument "test/repo"
        args, kwargs = total_func.call_args
        self.assertEqual(args, ("test/repo", "week"))
        self.assertDictEqual(kwargs, {})

        args, kwargs = passed_func.call_args
        self.assertEqual(args, ("test/repo", "week"))
        self.assertDictEqual(kwargs, {})

        total_func.return_value = 150
        self.assertEqual(50, get_pct_passed_build_jobs("test/repo", "week"))

        total_func.return_value = 0
        self.assertEqual(-1, get_pct_passed_build_jobs("test/repo", "week"))
        total_func.return_value = -1
        self.assertEqual(-1, get_pct_passed_build_jobs("test/repo", "week"))

        total_func.return_value = 100
        passed_func.return_value = 0
        self.assertEqual(0, get_pct_passed_build_jobs("test/repo", "week"))
        passed_func.return_value = -1
        self.assertEqual(-1, get_pct_passed_build_jobs("test/repo", "week"))

    @mock.patch('keen.add_event')
    def test_keen_add_event(self, add_event_func):
        """Test keenio.add_event()"""
        # test invalid parameters
        self.assertRaises(TypeError, keenio.keen_add_event)
        self.assertRaises(TypeError, keenio.keen_add_event, None)
        self.assertRaises(TypeError, keenio.keen_add_event, "collection", 123)
        self.assertRaises(
            TypeError, keenio.keen_add_event, "collection", "text"
        )
        self.assertRaises(TypeError, keenio.keen_add_event, "collection", [])

        # test keen_add_event with empty payload
        keenio.keen_add_event("collection", {})

        # check if mock was called with correct parameters
        args, kwargs = add_event_func.call_args
        self.assertEqual(args[0], "collection")
        self.assertDictEqual(args[1], {"buildtime_trend": self.project_info})
        self.assertDictEqual(kwargs, {})

        # test keen_add_event with payload
        keenio.keen_add_event("collection", {"test": "value"})

        # check if mock was called with correct parameters
        args, kwargs = add_event_func.call_args
        self.assertEqual(args[0], "collection")
        self.assertDictEqual(
            args[1],
            {
                "buildtime_trend": self.project_info,
                "test": "value"
            }
        )
        self.assertDictEqual(kwargs, {})

    @mock.patch('keen.add_events')
    def test_keen_add_events(self, add_events_func):
        """Test keenio.add_event()"""
        # test invalid parameters
        self.assertRaises(TypeError, keenio.keen_add_events)
        self.assertRaises(TypeError, keenio.keen_add_events, None)
        self.assertRaises(TypeError, keenio.keen_add_events, "collection", 123)
        self.assertRaises(
            TypeError, keenio.keen_add_events, "collection", "text"
        )
        self.assertRaises(TypeError, keenio.keen_add_events, "collection", {})

        # test keen_add_events with empty payload
        keenio.keen_add_events("collection", [])

        # check if mock was called with correct parameters
        args, kwargs = add_events_func.call_args
        self.assertEqual(args, ({"collection": []}, ))
        self.assertDictEqual(kwargs, {})

        # test keen_add_events with payload (1 item)
        keenio.keen_add_events("collection", [{"test": "value"}])

        # check if mock was called with correct parameters
        args, kwargs = add_events_func.call_args
        self.assertDictEqual(
            args[0],
            {"collection": [
                {
                    "buildtime_trend": self.project_info,
                    "test": "value"
                }
            ]}
        )
        self.assertDictEqual(kwargs, {})

        # test keen_add_events with payload (2 items)
        keenio.keen_add_events(
            "collection", [{"test": "value"}, {"test2": "value2"}]
        )

        # check if mock was called with correct parameters
        args, kwargs = add_events_func.call_args
        self.assertDictEqual(
            args[0],
            {"collection": [
                {
                    "buildtime_trend": self.project_info,
                    "test": "value"
                },
                {
                    "buildtime_trend": self.project_info,
                    "test2": "value2"
                }
            ]}
        )
        self.assertDictEqual(kwargs, {})

    @mock.patch('buildtimetrend.keenio.keen_add_event')
    @mock.patch('buildtimetrend.keenio.keen_add_events')
    def test_send_build_data(self, add_events_func, add_event_func):
        """Test keenio.send_build_data()"""
        # test invalid parameters
        self.assertRaises(TypeError, keenio.send_build_data)
        self.assertRaises(TypeError, keenio.send_build_data, None)
        self.assertRaises(TypeError, keenio.send_build_data, 123)
        self.assertRaises(TypeError, keenio.send_build_data, "text")
        self.assertRaises(TypeError, keenio.send_build_data, {})
        self.assertRaises(TypeError, keenio.send_build_data, [])

        buildjob = BuildJob()
        keenio.send_build_data(buildjob)

        # check if mock was called
        self.assertEqual(add_event_func.call_args, None)
        self.assertEqual(add_events_func.call_args, None)

        # set project id and write key
        keen.project_id = "1234abcd"
        keen.write_key = "1234abcd5678efgh"

        keenio.send_build_data(buildjob)

        # check if mock was called with correct parameters
        args, kwargs = add_event_func.call_args
        self.assertEqual(args[0], "build_jobs")
        self.assertDictEqual(
            args[1],
            {"job": {
                "duration": 0,
                "stages": []
            }}
        )
        self.assertDictEqual(kwargs, {})

        args, kwargs = add_events_func.call_args
        self.assertEqual(args[0], "build_stages")
        self.assertListEqual(args[1], [])
        self.assertDictEqual(kwargs, {})

        # test data_detail parameter = basic
        add_event_func.reset_mock()
        add_events_func.reset_mock()
        keenio.send_build_data(buildjob, 'basic')
        self.assertTrue(add_event_func.called)
        self.assertFalse(add_events_func.called)

        # test with "minimal" setting and "basic" override
        self.settings.add_setting("data_detail", "minimal")
        # test with "basic" override
        add_event_func.reset_mock()
        add_events_func.reset_mock()
        keenio.send_build_data(buildjob, 'basic')
        self.assertTrue(add_event_func.called)
        self.assertFalse(add_events_func.called)

        # test with "minimal" setting and "full" override
        add_event_func.reset_mock()
        add_events_func.reset_mock()
        keenio.send_build_data(buildjob, 'full')
        self.assertTrue(add_event_func.called)
        self.assertTrue(add_events_func.called)

        # test with "minimal" setting and no override
        add_event_func.reset_mock()
        add_events_func.reset_mock()
        keenio.send_build_data(buildjob)
        self.assertTrue(add_event_func.called)
        self.assertFalse(add_events_func.called)

    @mock.patch('buildtimetrend.keenio.keen_add_event')
    @mock.patch('buildtimetrend.keenio.keen_add_events')
    def test_send_build_data_service(self, add_events_func, add_event_func):
        """Test keenio.send_build_data_service()"""
        # test invalid parameters
        self.assertRaises(TypeError, keenio.send_build_data_service)
        self.assertRaises(TypeError, keenio.send_build_data_service, None)
        self.assertRaises(TypeError, keenio.send_build_data_service, 123)
        self.assertRaises(TypeError, keenio.send_build_data_service, "text")
        self.assertRaises(TypeError, keenio.send_build_data_service, {})
        self.assertRaises(TypeError, keenio.send_build_data_service, [])

        buildjob = BuildJob()
        keenio.send_build_data_service(buildjob)

        # check if mock was called
        self.assertEqual(add_event_func.call_args, None)
        self.assertEqual(add_events_func.call_args, None)

        # set project id and write key
        keen.project_id = "1234abcd"
        keen.write_key = "1234abcd5678efgh"

        keenio.send_build_data_service(buildjob)

        # check if mock was called with correct parameters
        args, kwargs = add_event_func.call_args
        self.assertEqual(args[0], "build_jobs")
        self.assertDictEqual(
            args[1],
            {"job": {
                "duration": 0,
                "stages": []
            }}
        )
        self.assertDictEqual(kwargs, {})

        args, kwargs = add_events_func.call_args
        self.assertEqual(args[0], "build_substages")
        self.assertListEqual(args[1], [])
        self.assertDictEqual(kwargs, {})

        # test data_detail parameter = basic
        add_event_func.reset_mock()
        add_events_func.reset_mock()
        keenio.send_build_data_service(buildjob, 'basic')
        self.assertTrue(add_event_func.called)
        self.assertFalse(add_events_func.called)

        # test with "minimal" setting and "basic" override
        self.settings.add_setting("data_detail", "minimal")
        # test with "basic" override
        add_event_func.reset_mock()
        add_events_func.reset_mock()
        keenio.send_build_data_service(buildjob, 'basic')
        self.assertTrue(add_event_func.called)
        self.assertFalse(add_events_func.called)

        # test with "minimal" setting and "full" override
        add_event_func.reset_mock()
        add_events_func.reset_mock()
        keenio.send_build_data_service(buildjob, 'full')
        self.assertTrue(add_event_func.called)
        self.assertTrue(add_events_func.called)

        # test with "minimal" setting and no override
        add_event_func.reset_mock()
        add_events_func.reset_mock()
        keenio.send_build_data_service(buildjob)
        self.assertTrue(add_event_func.called)
        self.assertFalse(add_events_func.called)
