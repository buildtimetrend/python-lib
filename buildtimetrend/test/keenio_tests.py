# vim: set expandtab sw=4 ts=4:
#
# Unit tests for Keen functions
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

from buildtimetrend.keenio import *
from buildtimetrend.settings import Settings
from buildtimetrend.tools import is_string
import os
import keen
import unittest
import mock
import constants


class TestKeen(unittest.TestCase):
    copy_keen_project_id = None
    copy_keen_write_key = None
    copy_keen_read_key = None
    copy_keen_master_key = None

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
        if "KEEN_MASTER_KEY" in os.environ:
            self.copy_keen_master_key = os.environ["KEEN_MASTER_KEY"]

    @classmethod
    def tearDownClass(self):
        # restore saved Keen.io environment variables
        if self.copy_keen_project_id is not None:
            os.environ["KEEN_PROJECT_ID"] = self.copy_keen_project_id
        if self.copy_keen_write_key is not None:
            os.environ["KEEN_WRITE_KEY"] = self.copy_keen_write_key
        if self.copy_keen_read_key is not None:
            os.environ["KEEN_READ_KEY"] = self.copy_keen_read_key
        if self.copy_keen_master_key is not None:
            os.environ["KEEN_MASTER_KEY"] = self.copy_keen_master_key

    def setUp(self):
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
        keen.project_id = None
        keen.write_key = None
        keen.read_key = None
        keen.master_key = None

    def raise_conn_err(*args, **kwargs):
        raise requests.ConnectionError

    def test_novalues(self):
        self.assertEqual(None, keen.project_id)
        self.assertEqual(None, keen.write_key)
        self.assertEqual(None, keen.read_key)
        self.assertEqual(None, keen.master_key)

        self.assertFalse(keen_has_project_id())
        self.assertFalse(keen_has_master_key())
        self.assertFalse(keen_has_write_key())
        self.assertFalse(keen_has_read_key())
        self.assertFalse(keen_is_writable())
        self.assertFalse(keen_is_readable())

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
            add_project_info_dict({
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
            add_project_info_dict({
                "test": "value",
                "job": {"finished_at": constants.SPLIT_TIMESTAMP_FINISHED}
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
        self.assertListEqual([
            {"test": "value", "buildtime_trend": self.project_info},
            {"test2": "value2", "buildtime_trend": self.project_info}],
            add_project_info_list([
                {"test": "value"},
                {"test2": "value2"}])
        )

    def test_keen_has_project_id_keen_var(self):
        keen.project_id = "1234abcd"

        self.assertTrue(keen_has_project_id())

    def test_keen_has_master_key_keen_var(self):
        keen.master_key = "abcd1234"
        keen.project_id = "1234abcd"

        self.assertTrue(keen_has_master_key())

    def test_keen_has_project_envir_vars(self):
        os.environ["KEEN_PROJECT_ID"] = "1234abcd"
        keen.project_id = "1234abcd"

        self.assertTrue(keen_has_project_id())

    def test_keen_has_master_key_env_vars(self):
        os.environ["KEEN_MASTER_KEY"] = "abcd1234"

        self.assertTrue(keen_has_master_key())

    def test_keen_is_writable_keen_var(self):
        # only set project id, check should fail
        keen.project_id = "1234abcd"

        self.assertFalse(keen_is_writable())

        # set write_key
        keen.write_key = "1234abcd5678efgh"

        self.assertTrue(keen_is_writable())

    def test_keen_is_writable_envir_vars(self):
        # only set project id, check should fail
        os.environ["KEEN_PROJECT_ID"] = "1234abcd"
        self.assertFalse(keen_is_writable())

        # set write_key
        os.environ["KEEN_WRITE_KEY"] = "1234abcd5678efgh"
        self.assertTrue(keen_is_writable())

    def test_keen_has_write_key_keen_var(self):
        # set write_key
        keen.write_key = "4567abcd5678efgh"
        self.assertTrue(keen_has_write_key())

    def test_keen_has_write_key_envir_vars(self):
        # set write_key
        os.environ["KEEN_WRITE_KEY"] = "4567abcd5678efgh"
        self.assertTrue(keen_has_write_key())

    def test_keen_has_read_key_keen_var(self):
        # set read_key
        keen.read_key = "4567abcd5678efgh"
        self.assertTrue(keen_has_read_key())

    def test_keen_has_read_key_envir_vars(self):
        # set read_key
        os.environ["KEEN_READ_KEY"] = "4567abcd5678efgh"
        self.assertTrue(keen_has_read_key())

    def test_keen_is_readable_keen_var(self):
        # only set project id, check should fail
        keen.project_id = "1234abcd"
        self.assertFalse(keen_is_readable())

        # set read_key
        keen.read_key = "4567abcd5678efgh"
        self.assertTrue(keen_is_readable())

    def test_keen_is_readable_envir_vars(self):
        # only set project id, check should fail
        os.environ["KEEN_PROJECT_ID"] = "1234abcd"
        self.assertFalse(keen_is_readable())

        # set read_key
        os.environ["KEEN_READ_KEY"] = "4567abcd5678efgh"
        self.assertTrue(keen_is_readable())

    def test_generate_read_key(self):
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
        # should return None if master key is not set
        self.assertEqual(None, keen_io_generate_write_key())

        # set master_key
        os.environ["KEEN_MASTER_KEY"] = "4567abcd5678efgh"
        self.assertTrue(isinstance(keen_io_generate_write_key(), bytes))

    def test_get_repo_filter(self):
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
        # empty or undefined defaults to 'week'
        self.assertDictEqual(
            {'name': 'week', 'timeframe': 'this_7_days', 'max_age': 600},
            check_time_interval()
        )
        self.assertDictEqual(
            {'name': 'week', 'timeframe': 'this_7_days', 'max_age': 600},
            check_time_interval(None)
        )
        self.assertDictEqual(
            {'name': 'week', 'timeframe': 'this_7_days', 'max_age': 600},
            check_time_interval(1234)
        )
        self.assertDictEqual(
            {'name': 'week', 'timeframe': 'this_7_days', 'max_age': 600},
            check_time_interval([])
        )

        # valid entries : week, month, year
        self.assertDictEqual(
            {'name': 'week', 'timeframe': 'this_7_days', 'max_age': 600},
            check_time_interval("week")
        )
        self.assertDictEqual(
            {'name': 'month', 'timeframe': 'this_30_days', 'max_age': 600},
            check_time_interval("month")
        )
        self.assertDictEqual(
            {'name': 'year', 'timeframe': 'this_52_weeks', 'max_age': 1800},
            check_time_interval("year")
        )

        # valid entries are case insensitive
        self.assertDictEqual(
            {'name': 'week', 'timeframe': 'this_7_days', 'max_age': 600},
            check_time_interval("wEEk")
        )
        self.assertDictEqual(
            {'name': 'month', 'timeframe': 'this_30_days', 'max_age': 600},
            check_time_interval("moNth")
        )

    def test_get_result_color(self):
        self.assertEqual("red", get_result_color())
        self.assertEqual("lightgrey", get_result_color(None))
        self.assertEqual("lightgrey", get_result_color(None, None))
        self.assertEqual("lightgrey", get_result_color(None, None, None))
        self.assertEqual("lightgrey", get_result_color(None))
        self.assertEqual("lightgrey", get_result_color(123, None))
        self.assertEqual("lightgrey", get_result_color(123, 34, None))
        self.assertEqual("lightgrey", get_result_color("string"))
        self.assertEqual("lightgrey", get_result_color(123, "string"))
        self.assertEqual("lightgrey", get_result_color(123, 34, "string"))

        # test 'OK' threshold
        self.assertEqual("green", get_result_color(100))
        self.assertEqual("green", get_result_color(100.0))
        self.assertEqual("green", get_result_color(91))
        self.assertEqual("green", get_result_color(90))
        self.assertEqual("green", get_result_color(90.0))

        # test 'warning' threshold
        self.assertEqual("yellow", get_result_color(89))
        self.assertEqual("yellow", get_result_color(89.9))
        self.assertEqual("yellow", get_result_color(71))
        self.assertEqual("yellow", get_result_color(70))
        self.assertEqual("yellow", get_result_color(70.0))

         # test 'error' threshold
        self.assertEqual("red", get_result_color(69))
        self.assertEqual("red", get_result_color(69.9))
        self.assertEqual("red", get_result_color(50))
        self.assertEqual("red", get_result_color(50.0))
        self.assertEqual("red", get_result_color(0))
        self.assertEqual("red", get_result_color(-10))

        # test custom thresholds
        self.assertEqual("green", get_result_color(100, 75, 50))
        self.assertEqual("green", get_result_color(76, 75, 50))
        self.assertEqual("green", get_result_color(75, 75, 50))
        self.assertEqual("yellow", get_result_color(74, 75, 50))
        self.assertEqual("yellow", get_result_color(51, 75, 50))
        self.assertEqual("yellow", get_result_color(50, 75, 50))
        self.assertEqual("red", get_result_color(49, 75, 50))
        self.assertEqual("red", get_result_color(0, 75, 50))
        self.assertEqual("red", get_result_color(-10, 75, 50))

    def test_has_build_id(self):
        # error is thrown when called without parameters
        self.assertRaises(ValueError, has_build_id)

        # error is thrown when called with an invalid parameter
        self.assertRaises(ValueError, has_build_id, None, None)

        # error is thrown when project_id or read key is not set
        self.assertRaises(SystemError, has_build_id, "test", 123)

        # test with an invalid token
        keen.project_id = "1234abcd"
        keen.read_key = "4567abcd5678efgh"
        self.assertRaises(SystemError, has_build_id, "test", 123)

    @mock.patch('keen.count', return_value=0)
    def test_has_build_id_mock(self, keen_count_func):
        # test with some token (value doesn't matter, keen.count is mocked)
        keen.project_id = "1234abcd"
        keen.read_key = "4567abcd5678efgh"
        # should return false if ID doesn't exist
        self.assertFalse(has_build_id("test", 123))

        # should return true if does exist
        keen_count_func.return_value = 1
        self.assertTrue(has_build_id("test", 123))

        # test raising ConnectionError
        keen_count_func.side_effect = self.raise_conn_err
        self.assertRaises(SystemError, has_build_id, "test", 123)

    @mock.patch(
        'buildtimetrend.keenio.keen_io_generate_read_key',
        return_value=None
    )
    def test_get_dashboard_keen_config(self, gen_key_func):
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

    def test_get_dashboard_config_dict(self):
        # error is thrown when extra parameter is not a dictionary
        self.assertRaises(
            TypeError,
            get_dashboard_config_dict, "test/repo", "should_be_dict"
        )

        # empty configuration
        self.assertDictEqual({}, get_dashboard_config_dict(""))

        # repo name is added
        self.assertDictEqual(
            {'projectName': 'test/repo', 'repoName': 'test/repo'},
            get_dashboard_config_dict("test/repo")
        )

        # add extra parameters
        self.assertEqual(
            {
                'projectName': 'test/repo', 'repoName': 'test/repo',
                'extra': 'value1', 'extra2': 'value2'
            },
            get_dashboard_config_dict(
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
        'buildtimetrend.keenio.get_dashboard_config_dict',
        return_value={'projectName': 'test/repo'}
    )
    def test_get_dashboard_config(self, config_dict_func, keen_config_func):
        self.assertEqual(
            "var config = {'projectName': 'test/repo'};"
            "\nvar keenConfig = {'projectId': '1234abcd'};",
            get_dashboard_config("test/repo")
        )

        # function was last called with argument "test/repo"
        args, kwargs = keen_config_func.call_args
        self.assertEqual(args, ("test/repo",))
        self.assertDictEqual(kwargs, {})

        print(config_dict_func.return_value)
        args, kwargs = config_dict_func.call_args
        self.assertEqual(args, ("test/repo", None))
        self.assertDictEqual(kwargs, {})

        # call function with argument "test/repo2"
        # and a dict with extra parameters
        get_dashboard_config("test/repo2", {'extra': 'value'})
        args, kwargs = keen_config_func.call_args
        self.assertEqual(args, ("test/repo2",))
        self.assertDictEqual(kwargs, {})

        args, kwargs = config_dict_func.call_args
        self.assertEqual(args, ("test/repo2", {'extra': 'value'}))
        self.assertDictEqual(kwargs, {})

    def test_get_avg_buildtime(self):
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
            'timeframe': TIME_INTERVALS['week']['timeframe'],
            'max_age': TIME_INTERVALS['week']['max_age'],
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
            'timeframe': TIME_INTERVALS['year']['timeframe'],
            'max_age': TIME_INTERVALS['year']['max_age'],
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
            'timeframe': TIME_INTERVALS['week']['timeframe'],
            'max_age': TIME_INTERVALS['week']['max_age'],
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
            'timeframe': TIME_INTERVALS['year']['timeframe'],
            'max_age': TIME_INTERVALS['year']['max_age'],
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
            'timeframe': TIME_INTERVALS['week']['timeframe'],
            'max_age': TIME_INTERVALS['week']['max_age'],
            'filters': [{
                'operator': 'eq',
                'property_name': 'buildtime_trend.project_name',
                'property_value': 'test/repo'
            },
            {
                "property_name": "job.result",
                "operator": "eq",
                "property_value": "passed"
            }]
        })

        self.assertEqual(34, get_passed_build_jobs("test/repo2", "year"))

        # test parameters passed to keen.average
        args, kwargs = keen_count_func.call_args
        self.assertEqual(args, ("build_jobs",))
        self.assertDictEqual(kwargs, {
            'target_property': 'job.job',
            'timeframe': TIME_INTERVALS['year']['timeframe'],
            'max_age': TIME_INTERVALS['year']['max_age'],
            'filters': [{
                'operator': 'eq',
                'property_name': 'buildtime_trend.project_name',
                'property_value': 'test/repo2'
            },
            {
                "property_name": "job.result",
                "operator": "eq",
                "property_value": "passed"
            }]
        })

        # test raising ConnectionError
        keen_count_func.side_effect = self.raise_conn_err
        self.assertEqual(-1, get_passed_build_jobs("test/repo"))

        # test raising KeenApiError (call with invalid read_key)
        patcher.stop()
        self.assertEqual(-1, get_passed_build_jobs("test/repo"))

    def test_get_total_builds(self):
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
            'timeframe': TIME_INTERVALS['week']['timeframe'],
            'max_age': TIME_INTERVALS['week']['max_age'],
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
            'timeframe': TIME_INTERVALS['year']['timeframe'],
            'max_age': TIME_INTERVALS['year']['max_age'],
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

        # return -1 if no value is returned
        keen_extract_func.return_value = []
        self.assertEqual(-1, get_latest_buildtime("test/repo"))

        # test raising ConnectionError
        keen_extract_func.side_effect = self.raise_conn_err
        self.assertEqual(-1, get_latest_buildtime("test/repo"))

        # test raising KeenApiError (call with invalid read_key)
        patcher.stop()
        self.assertEqual(-1, get_latest_buildtime("test/repo"))
