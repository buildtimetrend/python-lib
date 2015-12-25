# vim: set expandtab sw=4 ts=4:
#
# Unit tests for Settings
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

from buildtimetrend.settings import *
from buildtimetrend import logger
from buildtimetrend import set_loglevel
from buildtimetrend.collection import Collection
from buildtimetrend.keenio import keen_is_writable
from buildtimetrend.keenio import keen_is_readable
import buildtimetrend
import os
import keen
import unittest
import constants
import logging


DEFAULT_SETTINGS = {
    "project_name": buildtimetrend.NAME,
    "mode_native": False,
    "mode_keen": True,
    "loglevel": "WARNING",
    "multi_import": {
        "max_builds": 100,
        "delay": 3
    },
    "dashboard_configfile": "dashboard/config.js"
}


class TestSettings(unittest.TestCase):

    """Unit tests for Settings class"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixture."""
        cls.settings = Settings()

        cls.project_name = buildtimetrend.NAME

        cls.project_info = {
            "lib_version": buildtimetrend.VERSION,
            "schema_version": buildtimetrend.SCHEMA_VERSION,
            "client": 'None',
            "client_version": 'None',
            "project_name": cls.project_name}

    def setUp(self):
        """Initialise test environment before each test."""
        # reinit settings singleton
        if self.settings is not None:
            self.settings.__init__()

        set_loglevel("WARNING")

        keen._client = None
        keen.project_id = None
        keen.write_key = None
        keen.read_key = None
        keen.master_key = None

    def test_get_project_info(self):
        """Test Settings.get_project_info()"""
        self.assertDictEqual(
            self.project_info, self.settings.get_project_info()
        )

    def test_get_set_project_name(self):
        """Test Settings.set_project_info()"""
        self.assertEqual(self.project_name, self.settings.get_project_name())

        self.settings.set_project_name("test_name")
        self.assertEqual("test_name", self.settings.get_project_name())

        self.settings.set_project_name(None)
        self.assertEqual(None, self.settings.get_project_name())

        self.settings.set_project_name("")
        self.assertEqual("", self.settings.get_project_name())

    def test_set_client(self):
        """Test Settings.set_client()"""
        self.assertEqual(None, self.settings.get_setting("client"))
        self.assertEqual(None, self.settings.get_setting("client_version"))

        self.settings.set_client("client_name", "0.1")
        self.assertEqual("client_name", self.settings.get_setting("client"))
        self.assertEqual("0.1", self.settings.get_setting("client_version"))

        self.assertDictEqual({
            "lib_version": buildtimetrend.VERSION,
            "schema_version": buildtimetrend.SCHEMA_VERSION,
            "client": 'client_name',
            "client_version": '0.1',
            "project_name": self.project_name},
            self.settings.get_project_info()
        )

    def test_get_add_setting(self):
        """Test Settings.add_setting() and get_setting()"""
        # setting is not set yet
        self.assertEqual(None, self.settings.get_setting("test_name"))

        self.settings.add_setting("test_name", "test_value")
        self.assertEqual("test_value", self.settings.get_setting("test_name"))

        self.settings.add_setting("test_name", None)
        self.assertEqual(None, self.settings.get_setting("test_name"))

        self.settings.add_setting("test_name", "")
        self.assertEqual("", self.settings.get_setting("test_name"))

        self.settings.add_setting("test_name", 6)
        self.assertEqual(6, self.settings.get_setting("test_name"))

    def test_get_setting(self):
        """Test Settings.get_setting()"""
        self.assertEqual(None, self.settings.get_setting("test_name"))

        self.assertEqual(
            self.project_name,
            self.settings.get_setting("project_name"))

        self.assertDictEqual(DEFAULT_SETTINGS,
                             self.settings.settings.get_items())

    def test_no_config_file(self):
        """Test Settings.load_config_file() with an invalid file name"""
        # function should return false when file doesn't exist
        self.assertFalse(self.settings.load_config_file('no_file.yml'))
        self.assertDictEqual(DEFAULT_SETTINGS,
                             self.settings.settings.get_items())

        self.assertFalse(self.settings.load_config_file(''))
        self.assertDictEqual(DEFAULT_SETTINGS,
                             self.settings.settings.get_items())

        # function should throw an error when no filename is set
        self.assertRaises(TypeError, self.settings.load_config_file)

    def test_load_config_file(self):
        """Test Settings.load_config_file()"""
        # checking if Keen.io configuration is not set (yet)
        self.assertEqual(None, keen.project_id)
        self.assertEqual(None, keen.write_key)
        self.assertEqual(None, keen.read_key)
        self.assertEqual(None, keen.master_key)

        # load sample config file
        self.assertTrue(
            self.settings.load_config_file(constants.TEST_SAMPLE_CONFIG_FILE)
        )
        self.assertDictEqual(
            {
                "project_name": "test_project",
                "mode_native": True,
                "mode_keen": False,
                "loglevel": "INFO",
                "setting1": "test_value1",
                "dashboard_sample_configfile":
                constants.DASHBOARD_SAMPLE_CONFIG_FILE,
                "dashboard_configfile": "test/dashboard/config.js",
                "task_queue": {
                    "backend": "amqp",
                    "broker_url": "amqp://user@localhost"
                },
                "multi_import": {
                    "max_builds": 150,
                    "delay": 6
                }
            },
            self.settings.settings.get_items())

        # checking if Keen.io configuration is set
        self.assertEqual("1234", keen.project_id)
        self.assertEqual("12345678", keen.write_key)
        self.assertEqual("abcdefg", keen.read_key)
        self.assertEqual("7890abcd", keen.master_key)
        self.assertTrue(keen_is_readable())
        self.assertTrue(keen_is_writable())

    def test_load_multi_build_settings(self):
        """Test multi_import setting"""
        self.assertDictEqual(
            {
                "max_builds": 100,
                "delay": 3
            },
            self.settings.get_setting("multi_import")
        )

        exp_max_builds = os.environ["BTT_MULTI_MAX_BUILDS"] = "75"
        exp_max_builds = int(exp_max_builds)

        self.settings.load_env_vars()
        self.assertDictEqual(
            {
                "max_builds": exp_max_builds,
                "delay": 3
            },
            self.settings.get_setting("multi_import")
        )

        del os.environ["BTT_MULTI_MAX_BUILDS"]

    def test_load_settings(self):
        """Test Settings.load_settings()"""
        # checking if Keen.io configuration is not set (yet)
        self.assertEqual(None, keen.project_id)
        self.assertEqual(None, keen.write_key)
        self.assertEqual(None, keen.read_key)
        self.assertEqual(None, keen.master_key)

        scriptname = "script.py"
        expected_ci = "travis"
        expected_project_name = "test/project"

        argv = [
            scriptname,
            "--ci=%s" % expected_ci,
            "--repo=%s" % expected_project_name,
            "argument"
        ]

        exp_config = os.environ["BUILD_TREND_CONFIGFILE"] = "test/config.js"

        # load settings (config file, env vars and cli parameters)
        self.assertListEqual(
            ["argument"],
            self.settings.load_settings(argv,
                                        constants.TEST_SAMPLE_CONFIG_FILE)
        )
        self.assertDictEqual(
            {
                "project_name": expected_project_name,
                "ci_platform": expected_ci,
                "mode_native": True,
                "mode_keen": False,
                "loglevel": "INFO",
                "setting1": "test_value1",
                "dashboard_sample_configfile":
                constants.DASHBOARD_SAMPLE_CONFIG_FILE,
                "dashboard_configfile": exp_config,
                "task_queue": {
                    "backend": "amqp",
                    "broker_url": "amqp://user@localhost"
                },
                "multi_import": {
                    "max_builds": 150,
                    "delay": 6
                }
            },
            self.settings.settings.get_items())

        # checking if Keen.io configuration is set
        self.assertEqual("1234", keen.project_id)
        self.assertEqual("12345678", keen.write_key)
        self.assertEqual("abcdefg", keen.read_key)
        self.assertEqual("7890abcd", keen.master_key)
        self.assertTrue(keen_is_readable())
        self.assertTrue(keen_is_writable())

        del os.environ["BUILD_TREND_CONFIGFILE"]

    def test_env_var_to_settings(self):
        """Test Settings.env_var_to_settings()"""
        self.assertFalse(self.settings.env_var_to_settings("", ""))
        self.assertEqual(None, self.settings.get_setting("test"))
        self.assertFalse(self.settings.env_var_to_settings("NO_VAR", "test"))
        self.assertEqual(None, self.settings.get_setting("test"))

        os.environ["BTT_TEST_VAR"] = "test_value1"
        self.assertTrue(
            self.settings.env_var_to_settings("BTT_TEST_VAR", "test")
        )
        self.assertEqual("test_value1", self.settings.get_setting("test"))

        del os.environ["BTT_TEST_VAR"]

    def test_load_env_vars(self):
        """Test loading config env vars"""
        self.assertEqual("WARNING", self.settings.get_setting("loglevel"))
        self.assertEqual(
            None, self.settings.get_setting("travis_account_token")
        )

        # set test environment variables
        exp_account_token = os.environ["TRAVIS_ACCOUNT_TOKEN"] = "1234abcde"
        exp_loglevel = os.environ["BTT_LOGLEVEL"] = "INFO"
        exp_amqp = os.environ["BTT_AMQP_URL"] = "amqp://test@hostname:1234"
        exp_config = os.environ["BUILD_TREND_CONFIGFILE"] = "test/config.js"
        exp_max_builds = os.environ["BTT_MULTI_MAX_BUILDS"] = "50"
        exp_max_builds = int(exp_max_builds)
        exp_delay = os.environ["BTT_MULTI_DELAY"] = "5"
        exp_delay = int(exp_delay)

        self.settings.load_env_vars()

        # test environment variables
        self.assertEqual(exp_loglevel, self.settings.get_setting("loglevel"))
        self.assertEqual(
            exp_account_token,
            self.settings.get_setting("travis_account_token")
        )
        self.assertEqual(
            exp_config, self.settings.get_setting("dashboard_configfile")
        )
        self.assertDictEqual(
            {"backend": "amqp", "broker_url": exp_amqp},
            self.settings.get_setting("task_queue")
        )
        self.assertDictEqual(
            {"max_builds": exp_max_builds, "delay": exp_delay},
            self.settings.get_setting("multi_import")
        )

        # reset test environment variables
        del os.environ["BTT_LOGLEVEL"]
        del os.environ["BTT_AMQP_URL"]
        del os.environ["TRAVIS_ACCOUNT_TOKEN"]
        del os.environ["BUILD_TREND_CONFIGFILE"]
        del os.environ["BTT_MULTI_MAX_BUILDS"]
        del os.environ["BTT_MULTI_DELAY"]

    def test_load_env_vars_task_queue(self):
        """Test loading config env vars task queue"""
        # set test environment variables
        exp_redisgreen = os.environ["REDISGREEN_URL"] = \
            "redis://test@hostname:4567"

        self.settings.load_env_vars_task_queue()

        # test environment variables
        self.assertDictEqual(
            {"backend": "redis", "broker_url": exp_redisgreen},
            self.settings.get_setting("task_queue")
        )

        # set test environment variables
        exp_cloudamqp = os.environ["CLOUDAMQP_URL"] = \
            "amqp://guest:guest@localhost"

        self.settings.load_env_vars_task_queue()

        # test environment variables
        self.assertDictEqual(
            {"backend": "amqp", "broker_url": exp_cloudamqp},
            self.settings.get_setting("task_queue")
        )

        # set test environment variables
        exp_bigwig = os.environ["RABBITMQ_BIGWIG_URL"] = \
            "amqp://guest:guest@bigwig"

        self.settings.load_env_vars_task_queue()

        # test environment variables
        self.assertDictEqual(
            {"backend": "amqp", "broker_url": exp_bigwig},
            self.settings.get_setting("task_queue")
        )

        # set test environment variables
        exp_redis = os.environ["BTT_REDIS_URL"] = "redis://test@hostname:3456"

        self.settings.load_env_vars_task_queue()

        # test environment variables
        self.assertDictEqual(
            {"backend": "redis", "broker_url": exp_redis},
            self.settings.get_setting("task_queue")
        )

        # set test environment variables
        exp_amqp = os.environ["BTT_AMQP_URL"] = "amqp://test@hostname:2345"

        self.settings.load_env_vars_task_queue()

        # test environment variables
        self.assertDictEqual(
            {"backend": "amqp", "broker_url": exp_amqp},
            self.settings.get_setting("task_queue")
        )

        # remove first task queue url, second should be loaded
        del os.environ["BTT_AMQP_URL"]
        self.settings.load_env_vars_task_queue()

        # test environment variables
        self.assertDictEqual(
            {"backend": "redis", "broker_url": exp_redis},
            self.settings.get_setting("task_queue")
        )

        # reset test environment variables
        del os.environ["BTT_REDIS_URL"]
        del os.environ["RABBITMQ_BIGWIG_URL"]
        del os.environ["CLOUDAMQP_URL"]
        del os.environ["REDISGREEN_URL"]

    def test_process_argv(self):
        """Test processing cli arguments"""
        scriptname = "script.py"

        expected_ci = "travis"
        expected_build = "123"
        expected_job = "123.1"
        expected_branch = "branch1"
        expected_project_name = "test/project"
        expected_result = "passed"

        self.settings.add_setting("mode_keen", False)
        self.assertFalse(self.settings.get_setting("mode_keen"))
        self.assertFalse(self.settings.get_setting("mode_native"))
        self.assertEqual(logging.WARNING, logger.getEffectiveLevel())

        argv = [
            scriptname,
            "--log=INFO",
            "--ci=%s" % expected_ci,
            "--build=%s" % expected_build,
            "--job=%s" % expected_job,
            "--branch=%s" % expected_branch,
            "--repo=%s" % expected_project_name,
            "--result=%s" % expected_result,
            "--mode=keen",
            "--mode=native",
            "argument"
        ]

        self.assertListEqual(["argument"], self.settings.process_argv(argv))

        # test setting loglevel to WARNING
        self.assertEqual(logging.INFO, logger.getEffectiveLevel())
        # reset default loglevel
        set_loglevel("WARNING")

        # test other options
        self.assertEqual(
            expected_ci, self.settings.get_setting("ci_platform")
        )
        self.assertEqual(expected_build, self.settings.get_setting("build"))
        self.assertEqual(expected_job, self.settings.get_setting("job"))
        self.assertEqual(expected_branch, self.settings.get_setting("branch"))
        self.assertEqual(
            expected_project_name,
            self.settings.get_project_name()
        )
        self.assertEqual(expected_result, self.settings.get_setting("result"))
        self.assertTrue(self.settings.get_setting("mode_keen"))
        self.assertTrue(self.settings.get_setting("mode_native"))

        # no parameters
        self.assertListEqual([], self.settings.process_argv([scriptname]))
        self.assertEqual(None, self.settings.process_argv(None))

        # invalid parameters
        self.assertEqual(None, self.settings.process_argv([scriptname, "-x"]))
        self.assertEqual(
            None,
            self.settings.process_argv([scriptname, "--invalid"])
        )

        # help
        self.assertEqual(None, self.settings.process_argv([scriptname, "-h"]))
        self.assertEqual(
            None, self.settings.process_argv([scriptname, "--help"])
        )

    def test_set_mode(self):
        """Test setting operating mode"""
        self.assertTrue(self.settings.get_setting("mode_keen"))
        self.assertFalse(self.settings.get_setting("mode_native"))

        # test native mode
        self.settings.set_mode("native")
        self.assertTrue(self.settings.get_setting("mode_native"))
        self.settings.set_mode("native", False)
        self.assertFalse(self.settings.get_setting("mode_native"))
        self.settings.set_mode("native", True)
        self.assertTrue(self.settings.get_setting("mode_native"))
        self.settings.set_mode("native", 0)
        self.assertFalse(self.settings.get_setting("mode_native"))
        self.settings.set_mode("native", 1234)
        self.assertTrue(self.settings.get_setting("mode_native"))
        self.settings.set_mode("native", False)
        self.assertFalse(self.settings.get_setting("mode_native"))
        self.settings.set_mode("native", "1234")
        self.assertTrue(self.settings.get_setting("mode_native"))

        # test keen mode
        self.settings.set_mode("keen", False)
        self.assertFalse(self.settings.get_setting("mode_keen"))
        self.settings.set_mode("keen", True)
        self.assertTrue(self.settings.get_setting("mode_keen"))
        self.settings.set_mode("keen", False)
        self.assertFalse(self.settings.get_setting("mode_keen"))
        self.settings.set_mode("keen")
        self.assertTrue(self.settings.get_setting("mode_keen"))
