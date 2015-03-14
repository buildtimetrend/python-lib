# vim: set expandtab sw=4 ts=4:
#
# Unit tests for Trend class
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

import os
import buildtimetrend
from buildtimetrend.travis import *
from buildtimetrend.settings import Settings
from buildtimetrend.tools import get_repo_slug
import constants
import unittest

TRAVIS_TIMING_TAGS_FILE = "buildtimetrend/test/test_sample_travis_time_tags"
TRAVIS_INCORRECT_TIMING_TAGS_FILE = "buildtimetrend/test/test_sample_travis_time_tags_incorrect"
TRAVIS_LOG_FILE = "buildtimetrend/test/test_sample_travis_log"
TRAVIS_LOG_WORKER = "Using worker: worker-linux-12-1.bb.travis-ci.org:travis-linux-11"
TRAVIS_INCOMPLETE_LOG_WORKER = "Using worker: worker-linux-12-1.bb.travis-ci.org"

TEST_REPO = 'buildtimetrend/python-lib'
TEST_BUILD = '158'
VALID_HASH1 = '1234abcd'
VALID_HASH2 = '1234abce'
INVALID_HASH = 'abcd1234'
DURATION_NANO = 11000000000
DURATION_SEC = 11.0
DICT_BUILD_158 = {
    'branch': 'master',
    'build': '158',
    'ci_platform': 'travis',
    'job': '158.1',
    'repo': 'buildtimetrend/python-lib',
    'result': 'passed',
    'duration': 102.0,
    'worker': {
        'hostname': 'worker-linux-11-2.bb.travis-ci.org',
        'os': 'travis-linux-9'
    },
    'build_matrix': 'python',
    'language': 'python',
    'started_at': {
        'day_of_month': '08',
        'day_of_week': '2',
        'day_of_week_full_en': 'Tuesday',
        'day_of_week_short_en': 'Tue',
        'hour_12': '11',
        'hour_24': '11',
        'hour_ampm': 'AM',
        'isotimestamp': '2014-07-08T11:18:13+00:00',
        'microsecond': '000000',
        'minute': '18',
        'month': '07',
        'month_full_en': 'July',
        'month_short_en': 'Jul',
        'second': '13',
        'timestamp_seconds': 1404818293.0,
        'timezone': 'UTC',
        'timezone_offset': '+0000',
        'year': '2014'
    },
    'finished_at': {
        'day_of_month': '08',
        'day_of_week': '2',
        'day_of_week_full_en': 'Tuesday',
        'day_of_week_short_en': 'Tue',
        'hour_12': '11',
        'hour_24': '11',
        'hour_ampm': 'AM',
        'isotimestamp': '2014-07-08T11:19:55+00:00',
        'microsecond': '000000',
        'minute': '19',
        'month': '07',
        'month_full_en': 'July',
        'month_short_en': 'Jul',
        'second': '55',
        'timestamp_seconds': 1404818395.0,
        'timezone': 'UTC',
        'timezone_offset': '+0000',
        'year': '2014'
    }
}
DICT_BUILD_485 = [
{
    'branch': 'master',
    'build': '485',
    'ci_platform': 'travis',
    'job': '485.1',
    'repo': 'ruleant/getback_gps',
    'result': 'passed',
    'worker': {
        'hostname': 'worker-linux-7-1.bb.travis-ci.org',
        'os': 'travis-linux-7'},
    'build_matrix': 'java',
    'language': 'java',
    'started_at': {'day_of_month': '18',
        'day_of_week': '4',
        'day_of_week_full_en': 'Thursday',
        'day_of_week_short_en': 'Thu',
        'hour_12': '07',
        'hour_24': '19',
        'hour_ampm': 'PM',
        'isotimestamp': '2014-09-18T19:14:46+00:00',
        'microsecond': '000000',
        'minute': '14',
        'month': '09',
        'month_full_en': 'September',
        'month_short_en': 'Sep',
        'second': '46',
        'timestamp_seconds': 1411067686.0,
        'timezone': 'UTC',
        'timezone_offset': '+0000',
        'year': '2014'},
    'finished_at': {'day_of_month': '18',
        'day_of_week': '4',
        'day_of_week_full_en': 'Thursday',
        'day_of_week_short_en': 'Thu',
        'hour_12': '07',
        'hour_24': '19',
        'hour_ampm': 'PM',
        'isotimestamp': '2014-09-18T19:20:12+00:00',
        'microsecond': '000000',
        'minute': '20',
        'month': '09',
        'month_full_en': 'September',
        'month_short_en': 'Sep',
        'second': '12',
        'timestamp_seconds': 1411068012.0,
        'timezone': 'UTC',
        'timezone_offset': '+0000',
        'year': '2014'}},
{
    'branch': 'master',
    'build': '485',
    'ci_platform': 'travis',
    'job': '485.2',
    'repo': 'ruleant/getback_gps',
    'result': 'passed',
    'worker': {'hostname': 'worker-linux-3-2.bb.travis-ci.org',
        'os': 'travis-linux-7'},
    'build_matrix': 'java',
    'language': 'java',
    'started_at': {'day_of_month': '18',
        'day_of_week': '4',
        'day_of_week_full_en': 'Thursday',
        'day_of_week_short_en': 'Thu',
        'hour_12': '07',
        'hour_24': '19',
        'hour_ampm': 'PM',
        'isotimestamp': '2014-09-18T19:16:17+00:00',
        'microsecond': '000000',
        'minute': '16',
        'month': '09',
        'month_full_en': 'September',
        'month_short_en': 'Sep',
        'second': '17',
        'timestamp_seconds': 1411067777.0,
        'timezone': 'UTC',
        'timezone_offset': '+0000',
        'year': '2014'},
    'finished_at': {'day_of_month': '18',
        'day_of_week': '4',
        'day_of_week_full_en': 'Thursday',
        'day_of_week_short_en': 'Thu',
        'hour_12': '07',
        'hour_24': '19',
        'hour_ampm': 'PM',
        'isotimestamp': '2014-09-18T19:24:19+00:00',
        'microsecond': '000000',
        'minute': '24',
        'month': '09',
        'month_full_en': 'September',
        'month_short_en': 'Sep',
        'second': '19',
        'timestamp_seconds': 1411068259.0,
        'timezone': 'UTC',
        'timezone_offset': '+0000',
        'year': '2014'}}
]


class TestTravis(unittest.TestCase):
    def setUp(self):
        # reinit settings singleton
        Settings().__init__()

    def test_novalue(self):
        self.assertRaises(TypeError, convert_build_result)
        self.assertRaises(TypeError, convert_build_result, None)

    def test_load_travis_env_vars(self):
        settings = Settings()

        self.assertEquals(None, settings.get_setting("ci_platform"))
        self.assertEquals(None, settings.get_setting("build"))
        self.assertEquals(None, settings.get_setting("job"))
        self.assertEquals(None, settings.get_setting("branch"))
        self.assertEquals(None, settings.get_setting("result"))
        self.assertEquals(buildtimetrend.NAME, settings.get_project_name())

        #setup Travis env vars
        if "TRAVIS" in os.environ and os.environ["TRAVIS"] == "true":
            reset_travis_vars = False
            expected_build = os.environ["TRAVIS_BUILD_NUMBER"]
            expected_job = os.environ["TRAVIS_JOB_NUMBER"]
            expected_branch = os.environ["TRAVIS_BRANCH"]
            expected_project_name = os.environ["TRAVIS_REPO_SLUG"]
        else:
            reset_travis_vars = True
            os.environ["TRAVIS"] = "true"
            expected_build = os.environ["TRAVIS_BUILD_NUMBER"] = "123"
            expected_job = os.environ["TRAVIS_JOB_NUMBER"] = "123.1"
            expected_branch = os.environ["TRAVIS_BRANCH"] = "branch1"
            expected_project_name = os.environ["TRAVIS_REPO_SLUG"] = "test/project"

        # setup Travis test result
        if "TRAVIS_TEST_RESULT" in os.environ:
            reset_travis_result = False
            copy_result = os.environ["TRAVIS_TEST_RESULT"]
        else:
            reset_travis_result = True
        os.environ["TRAVIS_TEST_RESULT"] = "0"

        load_travis_env_vars()

        self.assertEquals("travis", settings.get_setting("ci_platform"))
        self.assertEquals(expected_build, settings.get_setting("build"))
        self.assertEquals(expected_job, settings.get_setting("job"))
        self.assertEquals(expected_branch, settings.get_setting("branch"))
        self.assertEquals(expected_project_name, settings.get_project_name())
        self.assertEquals("passed", settings.get_setting("result"))

        os.environ["TRAVIS_TEST_RESULT"] = "1"
        load_travis_env_vars()
        self.assertEquals("failed", settings.get_setting("result"))

        # reset test Travis vars
        if reset_travis_vars:
            del os.environ["TRAVIS"]
            del os.environ["TRAVIS_BUILD_NUMBER"]
            del os.environ["TRAVIS_JOB_NUMBER"]
            del os.environ["TRAVIS_BRANCH"]
            del os.environ["TRAVIS_REPO_SLUG"]

        # reset Travis test result
        if reset_travis_result:
            del os.environ["TRAVIS_TEST_RESULT"]
        else:
            os.environ["TRAVIS_TEST_RESULT"] = copy_result

    def test_convert_build_result(self):
        self.assertEquals("passed", convert_build_result(0))
        self.assertEquals("failed", convert_build_result(1))
        self.assertEquals("errored", convert_build_result(-1))
        self.assertEquals("errored", convert_build_result(2))

        self.assertEquals("passed", convert_build_result("0"))
        self.assertEquals("failed", convert_build_result("1"))
        self.assertEquals("errored", convert_build_result("-1"))
        self.assertEquals("errored", convert_build_result("2"))

    def test_process_notification_payload(self):
        settings = Settings()

        self.assertEquals(None, settings.get_setting("build"))
        self.assertEquals(buildtimetrend.NAME, settings.get_project_name())

        self.assertRaises(TypeError, process_notification_payload)
        self.assertRaises(ValueError, process_notification_payload, "")
        self.assertRaises(ValueError, process_notification_payload, "no_json")

        process_notification_payload(None)
        self.assertEquals(None, settings.get_setting("build"))
        self.assertEquals(buildtimetrend.NAME, settings.get_project_name())

        process_notification_payload(123)
        self.assertEquals(None, settings.get_setting("build"))
        self.assertEquals(buildtimetrend.NAME, settings.get_project_name())

        expected_build = '123'
        expected_owner = 'test'
        expected_repo = 'project'
        expected_project_name = get_repo_slug(expected_owner, expected_repo)

        # test with string
        process_notification_payload(
            '{"number": "%s", "repository": {"owner_name": "%s", "name": "%s"}}'
            % (expected_build, expected_owner, expected_repo)
        )

        self.assertEquals(expected_build, settings.get_setting("build"))
        self.assertEquals(expected_project_name, settings.get_project_name())

        # test with unicode string
        process_notification_payload(
            unicode('{"number": "%s", "repository": {"owner_name": "%s", "name": "%s"}}')
            % (expected_build, expected_owner, expected_repo)
        )

        self.assertEquals(expected_build, settings.get_setting("build"))
        self.assertEquals(expected_project_name, settings.get_project_name())

    def test_check_authorization(self):
        self.assertTrue(check_authorization(None, None))

        # set account token
        Settings().add_setting("travis_account_token", "co44eCtT0k3n")

        # test incorrect values
        self.assertFalse(check_authorization(None, None))
        self.assertFalse(check_authorization(TEST_REPO, None))
        self.assertFalse(check_authorization(None, "header1234"))
        self.assertFalse(check_authorization(TEST_REPO, "header1234"))

        # test correct Authorization header
        self.assertTrue(check_authorization(
            TEST_REPO,
            "61db633141cd24b4c9cbccb2a2c2c6a99988c3e346b951e4666e50474518cb82")
        )


class TestTravisData(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.travis_data = TravisData(TEST_REPO, TEST_BUILD)

    def test_novalue(self):
         # data should be empty
        self.assertEquals(0, len(self.travis_data.build_data))
        self.assertEquals(None, self.travis_data.get_started_at())
        self.assertEquals(None, self.travis_data.get_finished_at())
        self.assertEquals(None, self.travis_data.travis_substage)
        self.assertEquals(0, len(self.travis_data.build_jobs))
        self.assertEquals(0, len(self.travis_data.current_job.stages.stages))
        self.assertEquals(0, self.travis_data.current_job.properties.get_size())
        self.assertEquals(None, self.travis_data.current_job.stages.started_at)
        self.assertEquals(None, self.travis_data.current_job.stages.finished_at)

    def test_gather_data(self):
        # retrieve data from Travis API
        self.travis_data.get_build_data()
        self.assertTrue(len(self.travis_data.build_data) > 0)

        # retrieve start time
        self.assertEquals(
            '2014-07-08T11:18:13Z',
            self.travis_data.get_started_at())

        # retrieve finished timestamp
        self.assertEquals(
            '2014-07-08T11:19:55Z',
            self.travis_data.get_finished_at())

    def test_process_no_build_job(self):
        self.assertRaises(TypeError, self.travis_data.process_build_job)

        self.assertEquals(None, self.travis_data.process_build_job(None))
        self.assertEquals(0, len(self.travis_data.build_jobs))

    def test_process_build_job(self):
        build_job = self.travis_data.process_build_job("29404875")
        self.assertDictEqual(DICT_BUILD_158, build_job.properties.get_items())
        self.assertEquals(1, len(self.travis_data.build_jobs))
        self.assertDictEqual(DICT_BUILD_158,
            self.travis_data.build_jobs["29404875"].properties.get_items()
        )

    def test_process_no_build_jobs(self):
        # retrieve empty Travis API result
        self.travis_data.build_data = {"builds": [], "commits": []}
        self.travis_data.process_build_jobs()
        self.assertEquals(0, len(self.travis_data.build_jobs))

    def test_process_build_jobs(self):
        # retrieve data from Travis API
        self.travis_data.get_build_data()
        for build_job in self.travis_data.process_build_jobs():
            self.assertDictEqual(DICT_BUILD_158,
                build_job.properties.get_items())
        self.assertEquals(1, len(self.travis_data.build_jobs))
        self.assertDictEqual(DICT_BUILD_158,
            self.travis_data.build_jobs["29404875"].properties.get_items()
        )

    def test_process_build_two_jobs(self):
        self.travis_data = TravisData('ruleant/getback_gps', 485)
        self.assertEquals(0, len(self.travis_data.build_jobs))
        # retrieve data from Travis API
        self.travis_data.get_build_data()

        i = 0
        for build_job in self.travis_data.process_build_jobs():
            self.assertDictEqual(
                DICT_BUILD_485[i], build_job.properties.get_items()
            )
            i += 1

        self.assertEquals(2, len(self.travis_data.build_jobs))
        self.assertTrue("35665484" in self.travis_data.build_jobs)
        self.assertDictEqual(
            DICT_BUILD_485[0],
            self.travis_data.build_jobs["35665484"].properties.get_items()
        )
        self.assertTrue("35665485" in self.travis_data.build_jobs)
        self.assertDictEqual(
            DICT_BUILD_485[1],
            self.travis_data.build_jobs["35665485"].properties.get_items()
        )

    def test_nofile(self):
        # number of stages should be zero when file doesn't exist
        self.assertFalse(self.travis_data.parse_job_log_file('nofile.csv'))
        self.assertEquals(0, len(self.travis_data.current_job.stages.stages))

        self.assertFalse(self.travis_data.parse_job_log_file(''))
        self.assertEquals(0, len(self.travis_data.current_job.stages.stages))

    def test_parse_valid_job_log(self):
        self.travis_data.current_job.set_started_at("2014-08-17T13:40:14Z")
        # add a logfile with 4 stages
        self.assertTrue(self.travis_data.parse_job_log_file(TRAVIS_TIMING_TAGS_FILE))
        self.assertEquals(4, len(self.travis_data.current_job.stages.stages))

        self.assertEquals('install.4', self.travis_data.current_job.stages.stages[0]["name"])
        self.assertEquals('after_script.2', self.travis_data.current_job.stages.stages[1]["name"])
        self.assertEquals('after_script.3', self.travis_data.current_job.stages.stages[2]["name"])
        self.assertEquals('', self.travis_data.current_job.stages.stages[3]["name"])

        # check build started and finished timestamps
        self.assertEquals(1408282890.843066,
            self.travis_data.current_job.stages.started_at["timestamp_seconds"])
        self.assertEquals(1408282901.287937,
            self.travis_data.current_job.stages.finished_at["timestamp_seconds"])

    def test_parse_incorrect_job_log(self):
        self.travis_data.current_job.set_started_at("2014-08-17T13:40:14Z")
        # add a logfile with 2 incomplete stages and 2 valid stages
        self.assertTrue(self.travis_data.parse_job_log_file(TRAVIS_INCORRECT_TIMING_TAGS_FILE))
        self.assertEquals(2, len(self.travis_data.current_job.stages.stages))

        self.assertEquals('after_script.3', self.travis_data.current_job.stages.stages[0]["name"])
        self.assertEquals('', self.travis_data.current_job.stages.stages[1]["name"])

        # check build started and finished timestamps
        self.assertEquals(1408282901.278676,
            self.travis_data.current_job.stages.started_at["timestamp_seconds"])
        self.assertEquals(1408282901.287937,
            self.travis_data.current_job.stages.finished_at["timestamp_seconds"])

    def test_parse_valid_job_log_travis_sample(self):
        self.travis_data.current_job.set_started_at("2014-08-17T13:40:14Z")
        # add a sample Travis CI logfile
        self.assertTrue(self.travis_data.parse_job_log_file(TRAVIS_LOG_FILE))
        self._check_travis_log()

    def test_parse_travis_log(self):
        self.travis_data.current_job.set_started_at("2014-08-17T13:40:14Z")
        # retrieve and check Travis CI logfile
        self.travis_data.parse_job_log(32774630)
        self._check_travis_log()

    def _check_travis_log(self):
        # checks result of parsing a sample Travis CI log file
        self.assertEquals(18, len(self.travis_data.current_job.stages.stages))

        self.assertEquals('git.1', self.travis_data.current_job.stages.stages[0]["name"])
        self.assertEquals('', self.travis_data.current_job.stages.stages[1]["name"])
        self.assertEquals('git.3', self.travis_data.current_job.stages.stages[2]["name"])
        self.assertEquals('', self.travis_data.current_job.stages.stages[3]["name"])
        self.assertEquals('', self.travis_data.current_job.stages.stages[4]["name"])
        self.assertEquals('', self.travis_data.current_job.stages.stages[5]["name"])
        self.assertEquals('', self.travis_data.current_job.stages.stages[6]["name"])
        self.assertEquals('install.1', self.travis_data.current_job.stages.stages[7]["name"])
        self.assertEquals('install.2', self.travis_data.current_job.stages.stages[8]["name"])
        self.assertEquals('install.3', self.travis_data.current_job.stages.stages[9]["name"])
        self.assertEquals('install.4', self.travis_data.current_job.stages.stages[10]["name"])
        self.assertEquals('', self.travis_data.current_job.stages.stages[11]["name"])
        self.assertEquals('', self.travis_data.current_job.stages.stages[12]["name"])
        self.assertEquals('after_script.1', self.travis_data.current_job.stages.stages[13]["name"])
        self.assertEquals('after_script.2', self.travis_data.current_job.stages.stages[14]["name"])
        self.assertEquals('after_script.3', self.travis_data.current_job.stages.stages[15]["name"])
        self.assertEquals('after_script.4', self.travis_data.current_job.stages.stages[16]["name"])
        self.assertEquals('after_script.5', self.travis_data.current_job.stages.stages[17]["name"])

        # check build started and finished timestamps
        self.assertEquals(1408282815.329855,
            self.travis_data.current_job.stages.started_at["timestamp_seconds"])
        self.assertEquals(1408282905.966106,
            self.travis_data.current_job.stages.finished_at["timestamp_seconds"])

        # check worker tag
        self.assertDictEqual({'hostname': 'worker-linux-12-1.bb.travis-ci.org',
            'os': 'travis-linux-11'},
            self.travis_data.current_job.get_property("worker"))

    def test_parse_travis_time_tag(self):
        # read sample lines with timetags
        with open(TRAVIS_TIMING_TAGS_FILE, 'r') as f:
            """First stage"""
            # read next log file line
            self.travis_data.parse_travis_time_tag(f.next())

            # stage 'install.4' is started, but is not finished
            self.assertEquals(0, len(self.travis_data.current_job.stages.stages))
            self.assertTrue(self.travis_data.travis_substage.has_name())
            self.assertEquals('install.4', self.travis_data.travis_substage.get_name())
            self.assertTrue(self.travis_data.travis_substage.has_timing_hash())
            self.assertTrue(self.travis_data.travis_substage.has_command())
            self.assertTrue(self.travis_data.travis_substage.has_started())
            self.assertFalse(self.travis_data.travis_substage.has_finished())

            # read next log file line
            self.travis_data.parse_travis_time_tag(f.next())

            # stage 'install.4' is finished, and is added to Stages object
            self.assertEquals(1, len(self.travis_data.current_job.stages.stages))

            self.assertEquals('install.4', self.travis_data.current_job.stages.stages[0]["name"])
            self.assertEquals('CFLAGS="-O0" pip install -r requirements-tests.txt',
                self.travis_data.current_job.stages.stages[0]["command"])
            self.assertEquals('install.4', self.travis_data.current_job.stages.stages[0]["name"])
            self.assertEquals(1408282890.843066,
                self.travis_data.current_job.stages.stages[0]["started_at"]["timestamp_seconds"])
            self.assertEquals(1408282894.494005,
                self.travis_data.current_job.stages.stages[0]["finished_at"]["timestamp_seconds"])
            self.assertEquals(3.650939474, self.travis_data.current_job.stages.stages[0]["duration"])

            # check build started and finished timestamps
            self.assertEquals(
                1408282890.843066,
                self.travis_data.current_job.stages
                    .started_at["timestamp_seconds"])
            self.assertEquals(
                1408282894.494005,
                self.travis_data.current_job.stages
                    .finished_at["timestamp_seconds"])

            # new TravisSubstage object was created
            self.assertFalse(self.travis_data.travis_substage.has_name())
            self.assertFalse(
                self.travis_data.travis_substage.has_timing_hash()
            )
            self.assertFalse(self.travis_data.travis_substage.has_command())
            self.assertFalse(self.travis_data.travis_substage.has_started())
            self.assertFalse(self.travis_data.travis_substage.has_finished())

            """Seconds stage"""
            # read next log file line
            self.travis_data.parse_travis_time_tag(f.next())

            # stage 'after_script.2' is started, but is not finished
            self.assertEquals(
                1, len(self.travis_data.current_job.stages.stages)
            )
            self.assertTrue(self.travis_data.travis_substage.has_name())
            self.assertEquals(
                'after_script.2', self.travis_data.travis_substage.get_name()
            )
            self.assertTrue(self.travis_data.travis_substage.has_timing_hash())
            self.assertTrue(self.travis_data.travis_substage.has_command())
            self.assertTrue(self.travis_data.travis_substage.has_started())
            self.assertFalse(self.travis_data.travis_substage.has_finished())

            # read next log file line
            self.travis_data.parse_travis_time_tag(f.next())

            # stage 'after_script.2' is finished,
            # and is added to Stages object
            self.assertEquals(
                2, len(self.travis_data.current_job.stages.stages))

            self.assertEquals(
                'after_script.2',
                self.travis_data.current_job.stages.stages[1]["name"])
            self.assertEquals(
                'coveralls',
                self.travis_data.current_job.stages.stages[1]["command"])
            self.assertEquals(
                1408282896.480782,
                self.travis_data.current_job.stages
                    .stages[1]["started_at"]["timestamp_seconds"])
            self.assertEquals(
                1408282901.258724,
                self.travis_data.current_job.stages
                    .stages[1]["finished_at"]["timestamp_seconds"])
            self.assertEquals(
                4.777942342,
                self.travis_data.current_job.stages.stages[1]["duration"])

            # check build started and finished timestamps
            self.assertEquals(
                1408282890.843066,
                self.travis_data.current_job.stages
                    .started_at["timestamp_seconds"])
            self.assertEquals(
                1408282901.258724,
                self.travis_data.current_job.stages
                    .finished_at["timestamp_seconds"])

            """Third stage"""
            # new TravisSubstage object was created,
            # and the next stage is started
            self.assertTrue(self.travis_data.travis_substage.has_name())
            self.assertEquals(
                'after_script.3', self.travis_data.travis_substage.get_name()
            )
            self.assertFalse(
                self.travis_data.travis_substage.has_timing_hash()
            )
            self.assertTrue(self.travis_data.travis_substage.has_command())
            self.assertTrue(self.travis_data.travis_substage.has_started())
            self.assertFalse(self.travis_data.travis_substage.has_finished())

            # read next log file line
            self.travis_data.parse_travis_time_tag(f.next())

            # stage 'after_script.3' is finished, and is added to Stages object
            self.assertEquals(
                3, len(self.travis_data.current_job.stages.stages)
            )

            self.assertEquals(
                'after_script.3',
                self.travis_data.current_job.stages.stages[2]["name"]
            )
            self.assertEquals(
                'echo $TRAVIS_TEST_RESULT',
                self.travis_data.current_job.stages.stages[2]["command"]
            )
            self.assertFalse(
                'started_at' in self.travis_data.current_job.stages.stages[2]
            )
            self.assertFalse(
                'finished_at' in self.travis_data.current_job.stages.stages[2]
            )
            self.assertEquals(
                0, self.travis_data.current_job.stages.stages[2]["duration"])

            # check build started and finished timestamps, they don't change
            # because this stage doesn't having timing info
            self.assertEquals(
                1408282890.843066,
                self.travis_data.current_job.stages
                    .started_at["timestamp_seconds"])
            self.assertEquals(
                1408282901.258724,
                self.travis_data.current_job.stages
                    .finished_at["timestamp_seconds"])

            """Fourth stage"""
            # new TravisSubstage object was created,
            # and the next stage is started
            self.assertFalse(self.travis_data.travis_substage.has_name())
            self.assertEquals(
                'timestamp.sh Done',
                self.travis_data.travis_substage.get_name()
            )
            self.assertTrue(self.travis_data.travis_substage.has_timing_hash())
            self.assertTrue(self.travis_data.travis_substage.has_command())
            self.assertTrue(self.travis_data.travis_substage.has_started())
            self.assertFalse(self.travis_data.travis_substage.has_finished())

            # read next log file line
            self.travis_data.parse_travis_time_tag(f.next())

            # stage 'timestamp.sh Done' is finished,
            # and is added to Stages object
            self.assertEquals(
                4, len(self.travis_data.current_job.stages.stages))

            self.assertEquals(
                '', self.travis_data.current_job.stages.stages[3]["name"])
            self.assertEquals(
                'timestamp.sh Done',
                self.travis_data.current_job.stages.stages[3]["command"])
            self.assertEquals(
                1408282901.278676,
                self.travis_data.current_job.stages
                    .stages[3]["started_at"]["timestamp_seconds"])
            self.assertEquals(
                1408282901.287937,
                self.travis_data.current_job.stages
                    .stages[3]["finished_at"]["timestamp_seconds"])
            self.assertEquals(
                0.009261320,
                self.travis_data.current_job.stages.stages[3]["duration"])

            # check build started and finished timestamps
            self.assertEquals(
                1408282890.843066,
                self.travis_data.current_job.stages
                    .started_at["timestamp_seconds"])
            self.assertEquals(
                1408282901.287937,
                self.travis_data.current_job.stages
                    .finished_at["timestamp_seconds"])

    def test_parse_travis_time_tag_incorrect(self):
        # read sample lines with timetags
        with open(TRAVIS_INCORRECT_TIMING_TAGS_FILE, 'r') as f:
            """First stage"""
            # read next log file line
            self.travis_data.parse_travis_time_tag(f.next())

            # stage 'install.4' is started, but is not finished
            self.assertEquals(
                0, len(self.travis_data.current_job.stages.stages))
            self.assertTrue(self.travis_data.travis_substage.has_name())
            self.assertEquals('install.4',
                              self.travis_data.travis_substage.get_name())
            self.assertTrue(self.travis_data.travis_substage.has_timing_hash())
            self.assertTrue(self.travis_data.travis_substage.has_command())
            self.assertTrue(self.travis_data.travis_substage.has_started())
            self.assertFalse(self.travis_data.travis_substage.has_finished())

            # read next log file line
            self.travis_data.parse_travis_time_tag(f.next())

            # stage 'install.4' is not finished, end-tag is incorrect
            self.assertEquals(
                0, len(self.travis_data.current_job.stages.stages))

            # new TravisSubstage object was created
            self.assertFalse(self.travis_data.travis_substage.has_name())
            self.assertFalse(
                self.travis_data.travis_substage.has_timing_hash())
            self.assertFalse(self.travis_data.travis_substage.has_command())
            self.assertFalse(self.travis_data.travis_substage.has_started())
            self.assertFalse(self.travis_data.travis_substage.has_finished())

            # build started and finished timestamps are not set
            self.assertEquals(
                None, self.travis_data.current_job.stages.started_at)
            self.assertEquals(
                None, self.travis_data.current_job.stages.finished_at)

            """Seconds stage"""
            # read next log file line
            self.travis_data.parse_travis_time_tag(f.next())

            # stage 'after_script.2' is started, but is not finished
            self.assertEquals(
                0, len(self.travis_data.current_job.stages.stages))
            self.assertTrue(self.travis_data.travis_substage.has_name())
            self.assertEquals('after_script.2',
                              self.travis_data.travis_substage.get_name())
            self.assertTrue(self.travis_data.travis_substage.has_timing_hash())
            self.assertTrue(self.travis_data.travis_substage.has_command())
            self.assertTrue(self.travis_data.travis_substage.has_started())
            self.assertFalse(self.travis_data.travis_substage.has_finished())

            # read next log file line
            self.travis_data.parse_travis_time_tag(f.next())

            # stage 'after_script.3' is not finished,
            # because timing_hash is incorrect
            self.assertEquals(
                0, len(self.travis_data.current_job.stages.stages))

            # build started and finished timestamps are not set
            self.assertEquals(
                None, self.travis_data.current_job.stages.started_at)
            self.assertEquals(
                None, self.travis_data.current_job.stages.finished_at)

            """Third stage"""
            # new TravisSubstage object was created,
            # and the next stage is started
            self.assertTrue(self.travis_data.travis_substage.has_name())
            self.assertEquals(
                'after_script.3',
                self.travis_data.travis_substage.get_name())
            self.assertFalse(
                self.travis_data.travis_substage.has_timing_hash()
            )
            self.assertTrue(self.travis_data.travis_substage.has_command())
            self.assertTrue(self.travis_data.travis_substage.has_started())
            self.assertFalse(self.travis_data.travis_substage.has_finished())

            # read next log file line
            self.travis_data.parse_travis_time_tag(f.next())

            # stage 'after_script.3' is not finished,
            # because timing_hash is incorrect
            self.assertEquals(
                1,
                len(self.travis_data.current_job.stages.stages))

            self.assertEquals(
                'after_script.3',
                self.travis_data.current_job.stages.stages[0]["name"])
            self.assertEquals(
                'echo $TRAVIS_TEST_RESULT',
                self.travis_data.current_job.stages.stages[0]["command"])
            self.assertFalse(
                'started_at' in self.travis_data.current_job.stages.stages[0])
            self.assertFalse(
                'finished_at' in self.travis_data.current_job.stages.stages[0])
            self.assertEquals(
                0,
                self.travis_data.current_job.stages.stages[0]["duration"])

            # build started and finished timestamps are not set
            self.assertEquals(
                None, self.travis_data.current_job.stages.started_at)
            self.assertEquals(
                None, self.travis_data.current_job.stages.finished_at)

            """Fourth stage"""
            # new TravisSubstage object was created,
            # and the next stage is started
            self.assertFalse(self.travis_data.travis_substage.has_name())
            self.assertEquals(
                'timestamp.sh Done',
                self.travis_data.travis_substage.get_name())
            self.assertTrue(self.travis_data.travis_substage.has_timing_hash())
            self.assertTrue(self.travis_data.travis_substage.has_command())
            self.assertTrue(self.travis_data.travis_substage.has_started())
            self.assertFalse(self.travis_data.travis_substage.has_finished())

            # read next log file line
            self.travis_data.parse_travis_time_tag(f.next())

            # stage 'timestamp.sh Done' is finished,
            # and is added to Stages object
            self.assertEquals(
                2, len(self.travis_data.current_job.stages.stages)
            )

            self.assertEquals(
                '', self.travis_data.current_job.stages.stages[1]["name"]
            )
            self.assertEquals(
                'timestamp.sh Done',
                self.travis_data.current_job.stages.stages[1]["command"])
            self.assertEquals(
                1408282901.278676,
                self.travis_data.current_job.stages
                    .stages[1]["started_at"]["timestamp_seconds"])
            self.assertEquals(
                1408282901.287937,
                self.travis_data.current_job.stages
                    .stages[1]["finished_at"]["timestamp_seconds"])
            self.assertEquals(
                0.009261320,
                self.travis_data.current_job.stages.stages[1]["duration"])

            # check build started and finished timestamps
            self.assertEquals(
                1408282901.278676,
                self.travis_data.current_job.stages
                    .started_at["timestamp_seconds"])
            self.assertEquals(
                1408282901.287937,
                self.travis_data.current_job.stages
                    .finished_at["timestamp_seconds"])

    def test_parse_travis_worker_tag(self):
        # pass empty string
        self.travis_data.parse_travis_worker_tag("")
        self.assertEqual(None,
                         self.travis_data.current_job.get_property("worker"))

        # pass incomplete string
        self.travis_data.parse_travis_worker_tag(TRAVIS_INCOMPLETE_LOG_WORKER)
        self.assertEqual(None,
                         self.travis_data.current_job.get_property("worker"))

        # pass correct string
        self.travis_data.parse_travis_worker_tag(TRAVIS_LOG_WORKER)
        self.assertDictEqual(
            {
                'hostname': 'worker-linux-12-1.bb.travis-ci.org',
                'os': 'travis-linux-11'
            },
            self.travis_data.current_job.get_property("worker")
        )

    def test_has_timing_tags(self):
        """
        has_timing_tags() should be true if build was
        started at 2014-07-30 or after.
        """
        self.assertFalse(self.travis_data.has_timing_tags())

        self.travis_data.current_job.set_started_at("2014-07-29T16:30:00Z")
        self.assertFalse(self.travis_data.has_timing_tags())

        self.travis_data.current_job.set_started_at("2014-08-07T16:30:00Z")
        self.assertTrue(self.travis_data.has_timing_tags())

    def test_get_job_duration(self):
        """
        Calculate job duration.
        """
        self.assertAlmostEqual(0.0, self.travis_data.get_job_duration(), 0)

        self.travis_data.current_job.set_started_at("2014-07-30T16:30:00Z")
        self.assertAlmostEqual(0.0, self.travis_data.get_job_duration(), 0)

        self.travis_data.current_job.set_finished_at("2014-07-30T16:31:00Z")
        self.assertAlmostEqual(60.0, self.travis_data.get_job_duration(), 0)

        self.travis_data.current_job.set_finished_at(
            "2014-07-30T16:31:00.123Z"
        )
        self.assertAlmostEqual(60.123, self.travis_data.get_job_duration(), 3)

        # reset current_job and only set finished timestamp
        self.travis_data.current_job = Build()
        self.travis_data.current_job.set_finished_at(
            "2014-07-30T16:31:00.123Z"
        )
        self.assertAlmostEqual(0.0, self.travis_data.get_job_duration(), 0)


class TestTravisSubstage(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.substage = TravisSubstage()

    def test_novalue(self):
         # data should be empty
        self.assertFalse(self.substage.has_name())
        self.assertFalse(self.substage.has_timing_hash())
        self.assertFalse(self.substage.has_command())
        self.assertFalse(self.substage.has_started())
        self.assertFalse(self.substage.has_finished())
        self.assertFalse(self.substage.finished_incomplete)
        self.assertEquals("", self.substage.get_name())
        self.assertDictEqual(
            {"name": "", "duration": 0},
            self.substage.stage.to_dict())
        self.assertEquals("", self.substage.timing_hash)

    def test_param_is_not_dict(self):
        # error is thrown when called without parameters
        self.assertRaises(TypeError, self.substage.process_parsed_tags)
        self.assertRaises(TypeError, self.substage.process_start_stage)
        self.assertRaises(TypeError, self.substage.process_start_time)
        self.assertRaises(TypeError, self.substage.process_command)
        self.assertRaises(TypeError, self.substage.process_end_time)
        self.assertRaises(TypeError, self.substage.process_end_stage)

        # error is thrown when called with an invalid parameter
        self.assertRaises(TypeError, self.substage.process_parsed_tags, None)
        self.assertRaises(TypeError, self.substage.process_start_stage, None)
        self.assertRaises(TypeError, self.substage.process_start_time, None)
        self.assertRaises(TypeError, self.substage.process_command, None)
        self.assertRaises(TypeError, self.substage.process_end_time, None)
        self.assertRaises(TypeError, self.substage.process_end_stage, None)

        self.assertRaises(TypeError,
                          self.substage.process_parsed_tags, "string")
        self.assertRaises(TypeError,
                          self.substage.process_start_stage, "string")
        self.assertRaises(TypeError,
                          self.substage.process_start_time, "string")
        self.assertRaises(TypeError,
                          self.substage.process_command, "string")
        self.assertRaises(TypeError,
                          self.substage.process_end_time, "string")
        self.assertRaises(TypeError,
                          self.substage.process_end_stage, "string")

    def test_process_parsed_tags_full(self):
        # dict shouldn't be processed if it doesn't contain the required tags
        self.assertFalse(self.substage.process_parsed_tags(
            {'invalid': 'param'}
        ))
        self.assertFalse(self.substage.has_started())
        self.assertFalse(self.substage.has_finished())

        # dict shouldn't be processed if it doesn't contain the required tags
        self.assertFalse(self.substage.process_parsed_tags(
            {'start_stage': 'stage'}
        ))
        self.assertFalse(self.substage.has_started())
        self.assertFalse(self.substage.has_finished())

        # pass a valid start tag
        self.assertTrue(self.substage.process_parsed_tags({
            'start_stage': 'stage1', 'start_substage': 'substage1'
        }))
        self.assertTrue(self.substage.has_started())
        self.assertEquals("stage1.substage1", self.substage.stage.data["name"])
        self.assertFalse(self.substage.has_finished())

        # pass a valid timing hash
        self.assertTrue(self.substage.process_parsed_tags(
            {'start_hash': VALID_HASH1}
        ))
        self.assertTrue(self.substage.has_started())
        self.assertEquals(VALID_HASH1, self.substage.timing_hash)
        self.assertFalse(self.substage.has_finished())

        # pass a valid command name
        self.assertTrue(self.substage.process_parsed_tags(
            {'command': 'command1.sh'}
        ))
        self.assertTrue(self.substage.has_started())
        self.assertEquals('command1.sh', self.substage.stage.data["command"])
        self.assertFalse(self.substage.has_finished())

        # pass valid timing data
        self.assertTrue(self.substage.process_parsed_tags({
            'end_hash': VALID_HASH1,
            'start_timestamp': constants.TIMESTAMP_NANO_STARTED,
            'finish_timestamp': constants.TIMESTAMP_NANO_FINISHED,
            'duration': DURATION_NANO
        }))
        self.assertFalse(self.substage.has_finished())
        self.assertDictEqual(constants.SPLIT_TIMESTAMP_STARTED,
                             self.substage.stage.data["started_at"])
        self.assertDictEqual(constants.SPLIT_TIMESTAMP_FINISHED,
                             self.substage.stage.data["finished_at"])
        self.assertEquals(DURATION_SEC, self.substage.stage.data["duration"])

        # pass valid end tag
        self.assertTrue(self.substage.process_parsed_tags({
            'end_stage': 'stage1', 'end_substage': 'substage1'
        }))
        self.assertFalse(self.substage.finished_incomplete)
        self.assertTrue(self.substage.has_finished())

        # test stage
        self.assertDictEqual(
            {
                "name": "stage1.substage1",
                "duration": DURATION_SEC,
                "command": "command1.sh",
                "started_at": constants.SPLIT_TIMESTAMP_STARTED,
                "finished_at": constants.SPLIT_TIMESTAMP_FINISHED
            },
            self.substage.stage.to_dict()
        )

    def test_process_parsed_tags_no_starttag(self):
        # pass a valid timing hash
        self.assertTrue(
            self.substage.process_parsed_tags({'start_hash': VALID_HASH1})
        )
        self.assertTrue(self.substage.has_started())
        self.assertEquals(VALID_HASH1, self.substage.timing_hash)
        self.assertFalse(self.substage.has_finished())

        # pass a valid command name
        self.assertTrue(
            self.substage.process_parsed_tags({'command': 'command1.sh'})
        )
        self.assertTrue(self.substage.has_started())
        self.assertEquals('command1.sh', self.substage.stage.data["command"])
        self.assertFalse(self.substage.has_finished())

        # pass valid timing data
        self.assertTrue(self.substage.process_parsed_tags({
            'end_hash': VALID_HASH1,
            'start_timestamp': constants.TIMESTAMP_NANO_STARTED,
            'finish_timestamp': constants.TIMESTAMP_NANO_FINISHED,
            'duration': DURATION_NANO
        }))
        self.assertTrue(self.substage.has_finished())

        # test stage
        self.assertDictEqual(
            {
                # TODO assign substage name
                "name": "",
                "duration": DURATION_SEC,
                "command": "command1.sh",
                "started_at": constants.SPLIT_TIMESTAMP_STARTED,
                "finished_at": constants.SPLIT_TIMESTAMP_FINISHED
            },
            self.substage.stage.to_dict()
        )

    def test_process_parsed_tags_no_timing(self):
        # pass a valid start tag
        self.assertTrue(self.substage.process_parsed_tags({
            'start_stage': 'stage1', 'start_substage': 'substage1'
        }))
        self.assertTrue(self.substage.has_started())
        self.assertEquals("stage1.substage1", self.substage.stage.data["name"])
        self.assertFalse(self.substage.has_finished())

        # pass a valid command name
        self.assertTrue(
            self.substage.process_parsed_tags({'command': 'command1.sh'})
        )
        self.assertTrue(self.substage.has_started())
        self.assertEquals('command1.sh', self.substage.stage.data["command"])
        self.assertFalse(self.substage.has_finished())

        # pass valid end tag
        self.assertTrue(self.substage.process_parsed_tags({
            'end_stage': 'stage1', 'end_substage': 'substage1'
        }))
        self.assertFalse(self.substage.finished_incomplete)
        self.assertTrue(self.substage.has_finished())

        # test stage
        self.assertDictEqual(
            {
                "name": "stage1.substage1",
                "duration": 0.0,
                "command": "command1.sh",
            },
            self.substage.stage.to_dict()
        )

    def test_process_start_stage(self):
        # dict shouldn't be processed if it doesn't contain the required tags
        self.assertFalse(
            self.substage.process_start_stage({'invalid': 'param'})
        )
        self.assertFalse(
            self.substage.process_start_stage({'start_stage': 'stage'})
        )
        self.assertFalse(
            self.substage.process_start_stage({'start_substage': 'substage'})
        )

        # pass a valid start tag
        self.assertTrue(self.substage.process_start_stage({
            'start_stage': 'stage1', 'start_substage': 'substage1'
        }))
        self.assertTrue(self.substage.has_started())
        self.assertEquals("stage1.substage1", self.substage.stage.data["name"])
        self.assertFalse(self.substage.has_finished())

        # passing a valid start tag when it was started already, should fail
        self.assertFalse(self.substage.process_start_stage({
            'start_stage': 'stage1', 'start_substage': 'substage2'
        }))
        self.assertTrue(self.substage.has_started())
        self.assertEquals("stage1.substage1", self.substage.stage.data["name"])
        self.assertFalse(self.substage.has_finished())

    def test_process_start_time(self):
        # dict shouldn't be processed if it doesn't contain the required tags
        self.assertFalse(
            self.substage.process_start_time({'invalid': 'param'})
        )

        # pass a valid timing hash
        self.assertTrue(
            self.substage.process_start_time({'start_hash': VALID_HASH1})
        )
        self.assertTrue(self.substage.has_started())
        self.assertEquals(VALID_HASH1, self.substage.timing_hash)
        self.assertFalse(self.substage.has_finished())

        # passing a valid start tag when it was started already, should fail
        self.assertFalse(
            self.substage.process_start_time({'start_hash': VALID_HASH2})
        )
        self.assertTrue(self.substage.has_started())
        self.assertEquals(VALID_HASH1, self.substage.timing_hash)
        self.assertFalse(self.substage.has_finished())

    def test_process_command(self):
        # dict shouldn't be processed if it doesn't contain the required tags
        self.assertFalse(self.substage.process_command({'invalid': 'param'}))

        # call similar tests with a parameter
        self.__check_process_command('command1.sh')

    def test_process_command_has_name(self):
        # assign substage name
        self.substage.process_start_stage({
            'start_stage': 'stage1', 'start_substage': 'substage1'
        })

        # call similar tests with a parameter
        self.__check_process_command('stage1.substage1')

    def __check_process_command(self, expected_command):
        """similar test for test_process_command*"""
        # pass a valid command name
        self.assertTrue(
            self.substage.process_command({'command': 'command1.sh'})
        )
        self.assertTrue(self.substage.has_started())
        self.assertEquals('command1.sh', self.substage.stage.data["command"])
        self.assertEquals(expected_command, self.substage.get_name())

        # passing a valid command when it was started already, should fail
        self.assertFalse(
            self.substage.process_command({'command': 'command2.sh'})
        )
        self.assertTrue(self.substage.has_started())
        self.assertEquals('command1.sh', self.substage.stage.data["command"])
        self.assertEquals(expected_command, self.substage.get_name())

    def test_process_end_time_tags(self):
        # dict shouldn't be processed if it doesn't contain the required tags
        self.assertFalse(self.substage.process_end_time({'invalid': 'param'}))
        self.assertFalse(
            self.substage.process_end_time({'end_hash': VALID_HASH1})
        )
        self.assertFalse(
            self.substage.process_end_time(
                {'start_timestamp': constants.TIMESTAMP_NANO_STARTED}
            )
        )
        self.assertFalse(
            self.substage.process_end_time(
                {'finish_timestamp': constants.TIMESTAMP_NANO_FINISHED}
            )
        )
        self.assertFalse(
            self.substage.process_end_time({'duration': DURATION_NANO}))

    def test_process_end_time_not_started(self):
        # pass a valid start tag but, timing hasn't started
        self.assertFalse(self.substage.process_end_time({
            'end_hash': VALID_HASH1,
            'start_timestamp': constants.TIMESTAMP_NANO_STARTED,
            'finish_timestamp': constants.TIMESTAMP_NANO_FINISHED,
            'duration': DURATION_SEC
        }))
        self.assertTrue(self.substage.finished_incomplete)
        self.assertTrue(self.substage.has_finished())

    def test_process_end_time_invalid_hash(self):
        # timing has started, but hash doesn't match
        self.substage.process_start_time({'start_hash': VALID_HASH1})

        self.assertFalse(self.substage.process_end_time({
            'end_hash': INVALID_HASH,
            'start_timestamp': constants.TIMESTAMP_NANO_STARTED,
            'finish_timestamp': constants.TIMESTAMP_NANO_FINISHED,
            'duration': DURATION_NANO
        }))
        self.assertTrue(self.substage.finished_incomplete)
        self.assertTrue(self.substage.has_finished())

    def test_process_end_time_valid_hash(self):
        # timing has started, hash matches
        self.substage.process_start_time({'start_hash': VALID_HASH1})

        self.assertTrue(self.substage.process_end_time({
            'end_hash': VALID_HASH1,
            'start_timestamp': constants.TIMESTAMP_NANO_STARTED,
            'finish_timestamp': constants.TIMESTAMP_NANO_FINISHED,
            'duration': DURATION_NANO
        }))
        self.assertFalse(self.substage.finished_incomplete)
        self.assertTrue(self.substage.has_finished())

        self.assertDictEqual(constants.SPLIT_TIMESTAMP_STARTED,
                             self.substage.stage.data["started_at"])
        self.assertDictEqual(constants.SPLIT_TIMESTAMP_FINISHED,
                             self.substage.stage.data["finished_at"])
        self.assertEquals(DURATION_SEC, self.substage.stage.data["duration"])

    def test_process_end_stage_tags(self):
        # dict shouldn't be processed if it doesn't contain the required tags
        self.assertFalse(
            self.substage.process_end_stage({'invalid': 'param'}))
        self.assertFalse(
            self.substage.process_end_stage({'end_stage': 'stage1'}))
        self.assertFalse(
            self.substage.process_end_stage({'end_substage': 'substage1'}))

    def test_process_end_stage_not_started(self):
        # pass a valid end tag but, stage wasn't started
        self.assertFalse(self.substage.process_end_stage({
            'end_stage': 'stage1', 'end_substage': 'substage1'
        }))
        self.assertTrue(self.substage.finished_incomplete)
        self.assertTrue(self.substage.has_finished())

    def test_process_end_time_invalid_name(self):
        # stage was started, but name doesn't match
        self.substage.process_start_stage({
            'start_stage': 'stage1', 'start_substage': 'substage1'
        })

        self.assertFalse(self.substage.process_end_stage({
            'end_stage': 'stage1', 'end_substage': 'substage2'
        }))
        self.assertTrue(self.substage.finished_incomplete)
        self.assertTrue(self.substage.has_finished())

    def test_process_end_time_valid_name(self):
        # stage was started, name matches
        self.substage.process_start_stage({
            'start_stage': 'stage1', 'start_substage': 'substage1'
        })

        self.assertTrue(self.substage.process_end_stage({
            'end_stage': 'stage1', 'end_substage': 'substage1'
        }))
        self.assertFalse(self.substage.finished_incomplete)
        self.assertTrue(self.substage.has_finished())

    def test_get_name(self):
        """ get_name() returns the name, or the command if name is not set"""
        # set name
        self.substage.stage.set_name("stage.1")
        self.assertEquals("stage.1", self.substage.get_name())

        # set command, should have no influence, nam is already set
        self.substage.command = "command1.sh"
        self.assertEquals("stage.1", self.substage.get_name())

    def test_get_name_command(self):
        """ get_name() returns the name, or the command if name is not set"""
        # set command
        self.substage.stage.set_command("command1.sh")
        self.assertEquals("command1.sh", self.substage.get_name())

    def test_has_name(self):
        """ has_name() should return true if name is set"""
        # set name
        self.substage.stage.set_name("stage.1")
        self.assertTrue(self.substage.has_name())

    def test_has_timing_hash(self):
        """ has_started() should return true if timing_hash is set"""
        # set substage timing hash
        self.substage.timing_hash = VALID_HASH1
        self.assertTrue(self.substage.has_timing_hash())

    def test_has_command(self):
        """ has_command() should return true if command is set"""
        # set command
        self.substage.stage.set_command("command1.sh")
        self.assertTrue(self.substage.has_command())

    def test_has_started_name(self):
        """ has_started() should return true if name is set"""
        # set name
        self.substage.stage.set_name("stage.1")
        self.assertTrue(self.substage.has_started())

    def test_has_started_hash(self):
        """ has_started() should return true if timing_hash is set"""
        # set substage hash
        self.substage.timing_hash = VALID_HASH1
        self.assertTrue(self.substage.has_started())

    def test_has_started_command(self):
        """ has_started() should return true if command is set"""
        # set command
        self.substage.stage.set_command("command1.sh")
        self.assertTrue(self.substage.has_started())

    def test_has_started_both(self):
        """ has_started() should return true if name or hash is set"""
        # set name
        self.substage.name = "stage.1"
        # set timing hash
        self.substage.timing_hash = VALID_HASH1
        self.assertTrue(self.substage.has_started())

    def test_has_finished_stage_name(self):
        """ has_finished() should return true if stagename was closed"""
        self.substage.process_start_stage({
            'start_stage': 'stage1', 'start_substage': 'substage1'
        })

        self.assertTrue(self.substage.process_end_stage({
            'end_stage': 'stage1', 'end_substage': 'substage1'
        }))
        self.assertTrue(self.substage.has_finished())

    def test_has_finished_timestamp(self):
        """ has_finished() should return true if finished timestamp is set"""
        self.substage.process_start_time({'start_hash': VALID_HASH1})

        self.assertTrue(self.substage.process_end_time({
            'end_hash': VALID_HASH1,
            'start_timestamp': constants.TIMESTAMP_STARTED,
            'finish_timestamp': constants.TIMESTAMP_FINISHED,
            'duration': DURATION_NANO
        }))
        self.assertTrue(self.substage.has_finished())

    def test_has_finished_stage_command(self):
        """ has_finished() should return true if command is set"""
        self.substage.process_command({'command': 'command1.sh'})
        self.assertTrue(self.substage.has_finished())

    def test_has_finished_incomplete(self):
        """ has_finished() should return true if finished_incomplete is set"""
        # set finished_incomplete
        self.substage.finished_incomplete = True
        self.assertTrue(self.substage.has_finished())

    def test_has_finished(self):
        """
        has_finished() should return true if finished timestamp is set
        or if finished_incomplete is set
        """
        # set finish_timestamp
        self.substage.stage.set_finished_at = constants.TIMESTAMP_FINISHED
        # set finished_incomplete
        self.substage.finished_incomplete = True
        self.assertTrue(self.substage.has_finished())
