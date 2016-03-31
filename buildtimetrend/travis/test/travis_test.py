# vim: set expandtab sw=4 ts=4:
#
# Unit tests for Travis CI related functions and classes
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

import os
import json
import buildtimetrend
from builtins import str
from buildtimetrend.settings import Settings
from buildtimetrend.tools import get_repo_slug
from buildtimetrend.tools import check_dict
from buildtimetrend.travis import connector
from buildtimetrend.buildjob import BuildJob
from buildtimetrend.travis.parser import TravisData
from buildtimetrend.travis.connector import TravisConnector
from buildtimetrend.travis.tools import convert_build_result
from buildtimetrend.travis.tools import check_authorization
from buildtimetrend.travis.tools import process_notification_payload
from buildtimetrend.test import constants
import unittest

TRAVIS_TIMING_TAGS_FILE = "buildtimetrend/test/test_sample_travis_time_tags"
TRAVIS_INCORRECT_TIMING_TAGS_FILE = \
    "buildtimetrend/test/test_sample_travis_time_tags_incorrect"
TRAVIS_LOG_FILE = "buildtimetrend/test/test_sample_travis_log"
TRAVIS_LOG_WORKER = \
    "Using worker: worker-linux-12-1.bb.travis-ci.org:travis-linux-11"
TRAVIS_INCOMPLETE_LOG_WORKER = \
    "Using worker: worker-linux-12-1.bb.travis-ci.org"

TEST_REPO = 'buildtimetrend/python-lib'
TEST_BUILD = '158'
DICT_JOB_158_1 = {
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
    'build_matrix': {
        'summary': 'python 2.7',
        'language': 'python',
        'language_version': '2.7'
    },
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
DICT_BUILD_158 = DICT_JOB_158_1.copy()
DICT_BUILD_158.update({
    'build_trigger': "push",
    'pull_request': {
        'is_pull_request': False,
        'title': None,
        'number': None
    }
})
DICT_BUILD_485 = [
    {
        'branch': 'master',
        'build': '485',
        'ci_platform': 'travis',
        'job': '485.1',
        'repo': 'ruleant/getback_gps',
        'result': 'passed',
        'build_trigger': "push",
        'pull_request': {
            'is_pull_request': False,
            'title': None,
            'number': None
        },
        'worker': {
            'hostname': 'worker-linux-7-1.bb.travis-ci.org',
            'os': 'travis-linux-7'},
        'build_matrix': {
            'jdk': 'openjdk7',
            'summary': 'openjdk7 java',
            'language': 'java'
        },
        'started_at': {
            'day_of_month': '18',
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
        'finished_at': {
            'day_of_month': '18',
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
            'year': '2014'
        }
    },
    {
        'branch': 'master',
        'build': '485',
        'ci_platform': 'travis',
        'job': '485.2',
        'repo': 'ruleant/getback_gps',
        'result': 'passed',
        'build_trigger': "push",
        'pull_request': {
            'is_pull_request': False,
            'title': None,
            'number': None
        },
        'worker': {
            'hostname': 'worker-linux-3-2.bb.travis-ci.org',
            'os': 'travis-linux-7'
        },
        'build_matrix': {
            'jdk': 'oraclejdk8',
            'summary': 'oraclejdk8 java',
            'language': 'java'
        },
        'started_at': {
            'day_of_month': '18',
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
            'year': '2014'
        },
        'finished_at': {
            'day_of_month': '18',
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
            'year': '2014'
        }
    }
]
DICT_BUILD_504 = {
    'branch': 'master',
    'build': '504',
    'ci_platform': 'travis',
    'job': '504.1',
    'repo': 'buildtimetrend/python-lib',
    'result': 'passed',
    'build_trigger': "pull_request",
    'pull_request': {
        'is_pull_request': True,
        'title': "Keen master key",
        'number': 78
    },
    'worker': {
        'hostname': 'worker-linux-docker-77651b58.prod.travis-ci.org',
        'os': 'travis-linux-7'
    },
    'build_matrix': {
        'summary': 'python 2.7 linux',
        'os': 'linux',
        'language': 'python',
        'language_version': '2.7'
    },
    'started_at': {
        'day_of_month': '11',
        'day_of_week': '3',
        'day_of_week_full_en': 'Wednesday',
        'day_of_week_short_en': 'Wed',
        'hour_12': '08',
        'hour_24': '20',
        'hour_ampm': 'PM',
        'isotimestamp': '2015-02-11T20:24:34+00:00',
        'microsecond': '000000',
        'minute': '24',
        'month': '02',
        'month_full_en': 'February',
        'month_short_en': 'Feb',
        'second': '34',
        'timestamp_seconds': 1423686274.0,
        'timezone': 'UTC',
        'timezone_offset': '+0000',
        'year': '2015'
    },
    'finished_at': {
        'day_of_month': '11',
        'day_of_week': '3',
        'day_of_week_full_en': 'Wednesday',
        'day_of_week_short_en': 'Wed',
        'hour_12': '08',
        'hour_24': '20',
        'hour_ampm': 'PM',
        'isotimestamp': '2015-02-11T20:26:05+00:00',
        'microsecond': '000000',
        'minute': '26',
        'month': '02',
        'month_full_en': 'February',
        'month_short_en': 'Feb',
        'second': '05',
        'timestamp_seconds': 1423686365.0,
        'timezone': 'UTC',
        'timezone_offset': '+0000',
        'year': '2015'
    }
}

JOB_DATA_NO_LANG = '{"job":{"config":{"os":"osx","compiler":"clang"}}}'
JOB_DATA_C = '{"job":{"id":54285508,"repository_id":1181026,"repository_slug":"pyca/cryptography","build_id":54285507,"commit_id":15573583,"log_id":37201812,"number":"5501.1","config":{"language":"c","os":"osx","compiler":"clang","env":"TOXENV=py26","install":["./.travis/install.sh"],"script":["./.travis/run.sh"],"after_success":["source ~/.venv/bin/activate && coveralls"],"notifications":{"irc":{"channels":["irc.freenode.org#cryptography-dev"],"use_notice":true,"skip_join":true},"webhooks":["https://buildtimetrend.herokuapp.com/travis"]},".result":"configured"},"state":"passed","started_at":"2015-03-13T18:48:17Z","finished_at":"2015-03-13T19:01:54Z","queue":"builds.mac_osx","allow_failure":false,"tags":null,"annotation_ids":[]},"commit":{"id":15573583,"sha":"27be222667f9c4d9d7be383a9dd1f0cf1012daba","branch":"master","message":"support DER encoded EC private key serialization","committed_at":"2015-03-13T18:33:06Z","author_name":"Paul Kehrer","author_email":"paul.l.kehrer@gmail.com","committer_name":"Paul Kehrer","committer_email":"paul.l.kehrer@gmail.com","compare_url":"https://github.com/pyca/cryptography/pull/1755"},"annotations":[]}'
JOB_DATA_PYTHON = '{"job":{"id":54287645,"repository_id":1988445,"repository_slug":"buildtimetrend/python-lib","build_id":54287644,"commit_id":15574122,"log_id":37203465,"number":"536.1","config":{"language":"python","python":"2.7","sudo":false,"install":["CFLAGS=-O0 pip install -e .[native]","CFLAGS=-O0 pip install coveralls"],"script":["nosetests --with-coverage --cover-package=buildtimetrend"],"after_script":["coveralls"],"notifications":{"webhooks":["https://buildtimetrend-dev.herokuapp.com/travis","https://buildtimetrend.herokuapp.com/travis"]},".result":"configured","os":"linux","addons":{}},"state":"passed","started_at":"2015-03-13T18:50:00Z","finished_at":"2015-03-13T18:51:22Z","queue":"builds.docker","allow_failure":false,"tags":null,"annotation_ids":[]},"commit":{"id":15574122,"sha":"4055a820f0ac3cce2b59e2223316d9f32852ca4c","branch":"master","message":"fix coding style","committed_at":"2015-03-13T18:49:19Z","author_name":"Dieter Adriaenssens","author_email":"ruleant@users.sourceforge.net","committer_name":"Dieter Adriaenssens","committer_email":"ruleant@users.sourceforge.net","compare_url":"https://github.com/buildtimetrend/python-lib/compare/4903560d1840...4055a820f0ac"},"annotations":[]}'
JOB_DATA_JAVA = '{"job":{"id":35665484,"repository_id":1390431,"repository_slug":"ruleant/getback_gps","build_id":35665483,"commit_id":10254925,"log_id":23344586,"number":"485.1","config":{"language":"java","jdk":"openjdk7","before_install":["cd $HOME","if [[ -d buildtime-trend/.git ]]; then cd buildtime-trend; git pull; cd ..; else git clone https://github.com/ruleant/buildtime-trend.git; fi","source buildtime-trend/init.sh","mvn -v","timestamp.sh install_libs","sudo apt-get update -qq","sudo apt-get install -qq libstdc++6:i386 lib32z1 python-pip","timestamp.sh install_python_libs","sudo CFLAGS=-O0 pip install -r ${BUILD_TREND_HOME}/requirements.txt","timestamp.sh install_android_sdk","wget http://dl.google.com/android/android-sdk_r23.0.2-linux.tgz","tar -zxf android-sdk_r23.0.2-linux.tgz","export ANDROID_HOME=`pwd`/android-sdk-linux","export PATH=${PATH}:${ANDROID_HOME}/tools:${ANDROID_HOME}/platform-tools","echo y | android update sdk -a --filter tools,platform-tools,build-tools-20.0.0,android-20 --no-ui --force","$TRAVIS_BUILD_DIR/.utility/deploy-sdk-to-m2-repo.sh","cd $TRAVIS_BUILD_DIR","timestamp.sh build"],"script":["timestamp.sh test","mvn test -B"],"after_success":["timestamp.sh coverage","mvn clean test cobertura:cobertura coveralls:cobertura -B","timestamp.sh update_javadoc","mvn clean install javadoc:javadoc -DskipTests=true",".utility/copy-javadoc-to-gh-pages.sh"],"after_script":["timestamp.sh end","sync-buildtime-trend-with-gh-pages.sh"],"addons":{},".result":"configured","global_env":"GH_TOKEN=[secure] COVERITY_SCAN_TOKEN=[secure] KEEN_PROJECT_ID=[secure] KEEN_WRITE_KEY=[secure] KEEN_MASTER_KEY=[secure]"},"state":"passed","started_at":"2014-09-18T19:14:46Z","finished_at":"2014-09-18T19:20:12Z","queue":"builds.linux","allow_failure":false,"tags":null,"annotation_ids":[]},"commit":{"id":10254925,"sha":"0c3b9d9d710f299e20c7afa88cf4f1f53ae8e965","branch":"master","message":"wrap long line","committed_at":"2014-09-18T19:13:10Z","author_name":"Dieter Adriaenssens","author_email":"ruleant@users.sourceforge.net","committer_name":"Dieter Adriaenssens","committer_email":"ruleant@users.sourceforge.net","compare_url":"https://github.com/ruleant/getback_gps/compare/436484c2fd6a...0c3b9d9d710f"},"annotations":[]}'
JOB_DATA_ANDROID = '{"job":{"id":62985775,"repository_id":1390431,"repository_slug":"ruleant/getback_gps","build_id":62985773,"commit_id":17998453,"log_id":43745930,"number":"577.1","config":{"language":"android","android":{"components":["android-20","build-tools-21.1.2"]},"before_install":["cd $HOME","if [[ -d buildtime-trend/.git ]]; then cd buildtime-trend; git pull; cd ..; else git clone --recursive https://github.com/buildtimetrend/python-client.git buildtime-trend; fi","source buildtime-trend/init.sh","mvn -v","timestamp.sh install_libs","sudo apt-get update -qq","sudo apt-get install -qq python-pip","timestamp.sh install_python_libs","sudo CFLAGS=-O0 pip install -r ${BUILD_TREND_HOME}/requirements.txt","timestamp.sh deploy_android_sdk","$TRAVIS_BUILD_DIR/.utility/deploy-sdk-to-m2-repo.sh","cd $TRAVIS_BUILD_DIR"],"script":["timestamp.sh test","./gradlew clean check"],"after_success":["timestamp.sh coverage","mvn clean test cobertura:cobertura coveralls:cobertura -B","timestamp.sh update_javadoc","mvn clean install javadoc:javadoc -DskipTests=true",".utility/copy-javadoc-to-gh-pages.sh"],"after_script":["timestamp.sh end","sync-buildtime-trend-with-gh-pages.sh"],"addons":{},"notifications":{"webhooks":["https://buildtimetrend.herokuapp.com/travis","https://buildtimetrend-dev.herokuapp.com/travis"]},".result":"configured","global_env":"GH_TOKEN=[secure] COVERITY_SCAN_TOKEN=[secure] KEEN_PROJECT_ID=[secure] KEEN_WRITE_KEY=[secure] KEEN_MASTER_KEY=[secure]","os":"linux"},"state":"passed","started_at":"2015-05-18T08:56:53Z","finished_at":"2015-05-18T09:00:18Z","queue":"builds.linux","allow_failure":false,"tags":null,"annotation_ids":[]},"commit":{"id":17998453,"sha":"0f6f6f4af0b9c5013c9ebd1022780915e79a0701","branch":"master","message":"update bttaas url","committed_at":"2015-05-18T08:55:38Z","author_name":"Dieter Adriaenssens","author_email":"ruleant@users.sourceforge.net","committer_name":"Dieter Adriaenssens","committer_email":"ruleant@users.sourceforge.net","compare_url":"https://github.com/ruleant/getback_gps/compare/6de49007276c...0f6f6f4af0b9"},"annotations":[]}'


class TestTravis(unittest.TestCase):

    """Unit tests for Travis CI related functions and classes"""

    @staticmethod
    def setUp():
        """Initialise test environment before each test."""
        # reinit settings singleton
        Settings().__init__()

    def test_novalue(self):
        """Test freshly initialised Buildjob object."""
        self.assertRaises(TypeError, convert_build_result)
        self.assertRaises(TypeError, convert_build_result, None)

    def test_convert_build_result(self):
        """Test convert_build_result()"""
        self.assertEqual("passed", convert_build_result(0))
        self.assertEqual("failed", convert_build_result(1))
        self.assertEqual("errored", convert_build_result(-1))
        self.assertEqual("errored", convert_build_result(2))

        self.assertEqual("passed", convert_build_result("0"))
        self.assertEqual("failed", convert_build_result("1"))
        self.assertEqual("errored", convert_build_result("-1"))
        self.assertEqual("errored", convert_build_result("2"))

    def test_process_notification_payload(self):
        """Test process_notification_payload()"""
        settings = Settings()

        self.assertEqual(None, settings.get_setting("build"))
        self.assertEqual(buildtimetrend.NAME, settings.get_project_name())

        self.assertRaises(TypeError, process_notification_payload)
        self.assertRaises(ValueError, process_notification_payload, "")
        self.assertRaises(ValueError, process_notification_payload, "no_json")

        self.assertDictEqual({}, process_notification_payload(None))
        self.assertEqual(None, settings.get_setting("build"))
        self.assertEqual(buildtimetrend.NAME, settings.get_project_name())

        self.assertDictEqual({}, process_notification_payload(123))
        self.assertEqual(None, settings.get_setting("build"))
        self.assertEqual(buildtimetrend.NAME, settings.get_project_name())

        expected_build = '123'
        expected_owner = 'test'
        expected_repo = 'project'
        expected_project_name = get_repo_slug(expected_owner, expected_repo)

        # test with string
        self.assertDictEqual(
            {"repo": expected_project_name, "build": expected_build},
            process_notification_payload(
                '{{"number": "{0!s}", "repository": '
                '{{"owner_name": "{1!s}", "name": "{2!s}"}}}}'.format(
                    expected_build, expected_owner, expected_repo
                )
            )
        )

        self.assertEqual(expected_build, settings.get_setting("build"))
        self.assertEqual(expected_project_name, settings.get_project_name())

        # test with string, only containing repo info
        self.assertDictEqual(
            {"repo": expected_project_name},
            process_notification_payload(
                '{{"repository": {{"owner_name": "{0!s}"'
                ', "name": "{1!s}"}}}}'.format(expected_owner, expected_repo)
            )
        )

        # test with string, only containing build info
        self.assertDictEqual(
            {"build": expected_build},
            process_notification_payload(
                '{{"number": "{0!s}"}}'.format(expected_build)
            )
        )

        # test with unicode string
        self.assertDictEqual(
            {"repo": expected_project_name, "build": expected_build},
            process_notification_payload(
                u'{{"number": "{0!s}", "repository": '
                u'{{"owner_name": "{1!s}", "name": "{2!s}"}}}}'.format(
                    expected_build, expected_owner, expected_repo
                )
            )
        )

        self.assertEqual(expected_build, settings.get_setting("build"))
        self.assertEqual(expected_project_name, settings.get_project_name())

    def test_check_authorization(self):
        """Test check_authorization()"""
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
            "61db633141cd24b4c9cbccb2a2c2c6a99988c3e346b951e4666e50474518cb82"
        ))


class TestTravisData(unittest.TestCase):

    """Unit tests for TravisData class"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixture."""
        # show full diff in case of assert mismatch
        cls.maxDiff = None

    def setUp(self):
        """Initialise test environment before each test."""
        self.travis_data = TravisData(TEST_REPO, TEST_BUILD)

    def test_novalue(self):
        """Test freshly initialised Buildjob object."""
        # data should be empty
        self.assertEqual(0, len(self.travis_data.builds_data))
        self.assertEqual(None, self.travis_data.get_started_at())
        self.assertEqual(None, self.travis_data.get_finished_at())
        self.assertEqual(None, self.travis_data.travis_substage)
        self.assertEqual(0, len(self.travis_data.build_jobs))
        self.assertEqual(0, len(self.travis_data.current_job.stages.stages))
        self.assertEqual(
            0,
            self.travis_data.current_job.properties.get_size()
        )
        self.assertEqual(None, self.travis_data.current_job.stages.started_at)
        self.assertEqual(
            None,
            self.travis_data.current_job.stages.finished_at
        )

    def test_connector_parameter(self):
        """Test connector parameter"""
        self.assertEqual(
            connector.TRAVIS_ORG_API_URL, self.travis_data.connector.api_url
        )

        self.travis_data = TravisData(TEST_REPO, TEST_BUILD, 1234)
        self.assertEqual(
            connector.TRAVIS_ORG_API_URL, self.travis_data.connector.api_url
        )

        custom_connector = TravisConnector()
        custom_connector.api_url = "http://test.url.com/"
        self.travis_data = TravisData(TEST_REPO, TEST_BUILD, custom_connector)
        self.assertEqual(
            "http://test.url.com/", self.travis_data.connector.api_url
        )

    def test_get_build_data(self):
        """Test TravisData.get_build_data() with invalid url"""
        self.assertTrue(self.travis_data.get_build_data())

        # trigger URLError, with invalid URL
        self.travis_data.connector.api_url = "http://invalid_url/"
        self.assertFalse(self.travis_data.get_build_data())

    def test_gather_data(self):
        """Test TravisData.get_build_data()"""
        # retrieve data from Travis API
        self.assertTrue(self.travis_data.get_build_data())
        self.assertTrue(
            check_dict(self.travis_data.builds_data, key_list=["builds"])
        )
        self.assertTrue(len(self.travis_data.builds_data["builds"]) > 0)
        self.assertTrue(
            check_dict(
                self.travis_data.builds_data["builds"][0],
                key_list=[
                    "id", "number", "job_ids", "config",
                    "started_at", "finished_at"
                ]
            )
        )

        # there should be build job IDs
        self.assertTrue(
            len(self.travis_data.builds_data["builds"][0]["job_ids"]) > 0
        )

        # check build number
        self.assertEqual(
            '158',
            self.travis_data.builds_data["builds"][0]["number"]
        )

        # retrieve start time
        self.assertEqual(
            '2014-07-08T11:18:13Z',
            self.travis_data.builds_data["builds"][0]["started_at"])

        # retrieve finished timestamp
        self.assertEqual(
            '2014-07-08T11:19:55Z',
            self.travis_data.builds_data["builds"][0]["finished_at"])

    def test_get_started_at(self):
        """Test TravisData.get_started_at()"""
        self.travis_data.current_build_data = {
            "started_at": '2014-07-08T11:18:13Z',
        }

        # retrieve start time
        self.assertEqual(
            '2014-07-08T11:18:13Z',
            self.travis_data.get_started_at())

    def test_get_finished_at(self):
        """Test TravisData.get_finished_at()"""
        self.travis_data.current_build_data = {
            "finished_at": '2014-07-08T11:19:55Z'
        }

        # retrieve finished timestamp
        self.assertEqual(
            '2014-07-08T11:19:55Z',
            self.travis_data.get_finished_at())

    def test_get_substage_name(self):
        """Test TravisData.get_substage_name()"""
        # test missing parameter
        self.assertRaises(TypeError, self.travis_data.get_substage_name)

        # test incorrect parameter
        self.assertEqual("", self.travis_data.get_substage_name(123))
        self.assertEqual("", self.travis_data.get_substage_name([]))
        self.assertEqual("", self.travis_data.get_substage_name({}))

        # result should be empty if no build config data is set
        self.assertEqual(
            "", self.travis_data.get_substage_name("test_command.sh")
        )

        # test with incorrect build config data
        self.travis_data.current_build_data = {"test": "value"}
        self.assertEqual(
            "", self.travis_data.get_substage_name("test_command.sh")
        )

        # test with empty command list
        self.travis_data.current_build_data = {"config": {}}
        self.assertEqual(
            "", self.travis_data.get_substage_name("test_command.sh")
        )

        # test with correct build data, but without a matching command
        self.travis_data.current_build_data = \
            json.loads(JOB_DATA_ANDROID)["job"]
        self.assertEqual(
            "", self.travis_data.get_substage_name("test_command.sh")
        )

        # test with existing command
        self.assertEqual(
            "before_install.4", self.travis_data.get_substage_name("mvn -v")
        )

    def test_process_no_build_job(self):
        """Test TravisData.process_build_job() with invalid parameters"""
        self.assertRaises(TypeError, self.travis_data.process_build_job)

        self.assertEqual(None, self.travis_data.process_build_job(None))
        self.assertEqual(0, len(self.travis_data.build_jobs))

    def test_process_build_job(self):
        """Test TravisData.process_build_job()"""
        build_job = self.travis_data.process_build_job("29404875")
        self.assertDictEqual(DICT_JOB_158_1, build_job.properties.get_items())
        self.assertEqual(1, len(self.travis_data.build_jobs))
        self.assertDictEqual(
            DICT_JOB_158_1,
            self.travis_data.build_jobs["29404875"].properties.get_items()
        )

    def test_process_no_build_jobs(self):
        """Test TravisData.process_build_jobs() with no build jobs"""
        # retrieve empty Travis API result
        self.travis_data.builds_data = {"builds": [], "commits": []}
        self.travis_data.process_build_jobs()
        self.assertEqual(0, len(self.travis_data.build_jobs))

    def test_process_build_jobs(self):
        """Test TravisData.process_build_jobs() with no build jobs"""
        # retrieve data from Travis API
        self.travis_data.get_build_data()
        for build_job in self.travis_data.process_build_jobs():
            self.assertDictEqual(
                DICT_BUILD_158,
                build_job.properties.get_items()
            )
        self.assertEqual(1, len(self.travis_data.build_jobs))
        self.assertDictEqual(
            DICT_BUILD_158,
            self.travis_data.build_jobs["29404875"].properties.get_items()
        )

    def test_process_build_two_jobs(self):
        """Test TravisData.process_build_jobs() with two jobs"""
        self.travis_data = TravisData('ruleant/getback_gps', 485)
        self.assertEqual(0, len(self.travis_data.build_jobs))
        # retrieve data from Travis API
        self.travis_data.get_build_data()

        i = 0
        for build_job in self.travis_data.process_build_jobs():
            self.assertDictEqual(
                DICT_BUILD_485[i], build_job.properties.get_items()
            )
            i += 1

        self.assertEqual(2, len(self.travis_data.build_jobs))
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

    def test_process_build_jobs_pull_request(self):
        """Test TravisData.process_build_jobs() of a pull request"""
        self.travis_data = TravisData('buildtimetrend/python-lib', 504)
        self.assertEqual(0, len(self.travis_data.build_jobs))

        # retrieve data from Travis API
        self.travis_data.get_build_data()
        for build_job in self.travis_data.process_build_jobs():
            self.assertDictEqual(
                DICT_BUILD_504,
                build_job.properties.get_items()
            )
        self.assertEqual(1, len(self.travis_data.build_jobs))
        self.assertDictEqual(
            DICT_BUILD_504,
            self.travis_data.build_jobs["50398739"].properties.get_items()
        )

    def test_no_pull_request_data(self):
        """Test TravisData.process_pull_request_data() with no data"""
        self.travis_data.current_build_data = {"test_value": "empty"}

        self.travis_data.process_pull_request_data()

        # retrieve pull request data
        self.assertDictEqual(
            {'is_pull_request': False},
            self.travis_data.current_job.get_property("pull_request")
        )

    def test_pull_request_data(self):
        """Test TravisData.process_pull_request_data() with valid data"""
        self.travis_data.current_build_data = {
            "pull_request": True,
            "pull_request_title": "Test message",
            "pull_request_number": 345
        }

        self.travis_data.process_pull_request_data()

        # retrieve start time
        self.assertDictEqual(
            {
                'is_pull_request': True,
                'title': "Test message",
                'number': 345
            },
            self.travis_data.current_job.get_property("pull_request")
        )

    def test_get_build_matrix_no_job_data(self):
        """Test TravisData.set_build_matrix without job data"""
        self.travis_data.set_build_matrix(json.loads('{}'))
        self.assertDictEqual(
            {},
            self.travis_data.current_job.properties.get_items()
        )

    def test_get_build_matrix_no_config_data(self):
        """Test TravisData.set_build_matrix without config data"""
        self.travis_data.set_build_matrix(json.loads('{"job":{}}'))
        self.assertDictEqual(
            {},
            self.travis_data.current_job.properties.get_items()
        )

    def test_get_build_matrix_no_lang(self):
        """Test TravisData.set_build_matrix with no language tag"""
        self.travis_data.set_build_matrix(json.loads(JOB_DATA_NO_LANG))
        self.assertDictEqual(
            {
                'build_matrix': {
                    'compiler': 'clang',
                    'os': 'osx',
                    'summary': 'clang osx'
                }
            },
            self.travis_data.current_job.properties.get_items())

    def test_get_build_matrix_c(self):
        """Test TravisData.set_build_matrix of a C project"""
        self.travis_data.set_build_matrix(json.loads(JOB_DATA_C))
        self.assertDictEqual(
            {
                'build_matrix': {
                    'compiler': 'clang',
                    'language': 'c',
                    'os': 'osx',
                    'parameters': 'TOXENV=py26',
                    'summary': 'clang c osx TOXENV=py26'
                }
            },
            self.travis_data.current_job.properties.get_items())

    def test_get_build_matrix_python(self):
        """Test TravisData.set_build_matrix of a Python project"""
        self.travis_data.set_build_matrix(json.loads(JOB_DATA_PYTHON))
        self.assertDictEqual(
            {
                'build_matrix': {
                    'os': 'linux',
                    'language': 'python',
                    'language_version': '2.7',
                    'summary': 'python 2.7 linux'
                }
            },
            self.travis_data.current_job.properties.get_items())

    def test_get_build_matrix_java(self):
        """Test TravisData.set_build_matrix of a Java project"""
        self.travis_data.set_build_matrix(json.loads(JOB_DATA_JAVA))
        self.assertDictEqual(
            {
                'build_matrix': {
                    'jdk': 'openjdk7',
                    'language': 'java',
                    'summary': 'openjdk7 java'
                }
            },
            self.travis_data.current_job.properties.get_items())

    def test_get_build_matrix_android(self):
        """Test TravisData.set_build_matrix of an Android project"""
        self.travis_data.set_build_matrix(json.loads(JOB_DATA_ANDROID))
        self.assertDictEqual(
            {
                'build_matrix': {
                    'language': 'android',
                    'language_components': 'android-20 build-tools-21.1.2',
                    'os': 'linux',
                    'summary': 'android android-20 build-tools-21.1.2 linux'
                }
            },
            self.travis_data.current_job.properties.get_items())

    def test_no_logfile(self):
        """
        Test TravisData.parse_job_log_file() with an invalid or empty file
        """
        # number of stages should be zero when file doesn't exist
        self.assertFalse(self.travis_data.parse_job_log_file('nofile.csv'))
        self.assertEqual(0, len(self.travis_data.current_job.stages.stages))

        self.assertFalse(self.travis_data.parse_job_log_file(''))
        self.assertEqual(0, len(self.travis_data.current_job.stages.stages))

    def test_parse_valid_job_log(self):
        """Test TravisData.parse_job_log_file()"""
        self.travis_data.current_job.set_started_at("2014-08-17T13:40:14Z")
        # add a logfile with 4 stages
        self.assertTrue(
            self.travis_data.parse_job_log_file(TRAVIS_TIMING_TAGS_FILE)
        )
        self.assertEqual(4, len(self.travis_data.current_job.stages.stages))

        self.assertEqual(
            'install.4',
            self.travis_data.current_job.stages.stages[0]["name"]
        )
        self.assertEqual(
            'after_script.2',
            self.travis_data.current_job.stages.stages[1]["name"]
        )
        self.assertEqual(
            'after_script.3',
            self.travis_data.current_job.stages.stages[2]["name"]
        )
        self.assertEqual(
            '',
            self.travis_data.current_job.stages.stages[3]["name"]
        )

        # check build started and finished timestamps
        self.assertEqual(
            1408282890.843065,
            self.travis_data.current_job.stages
                .started_at["timestamp_seconds"]
        )
        self.assertEqual(
            1408282901.287937,
            self.travis_data.current_job.stages
                .finished_at["timestamp_seconds"]
        )

    def test_parse_incorrect_job_log(self):
        """Test TravisData.parse_job_log_file() with incomplete timing tags"""
        self.travis_data.current_job.set_started_at("2014-08-17T13:40:14Z")
        # add a logfile with 2 incomplete stages and 2 valid stages
        self.assertTrue(
            self.travis_data.parse_job_log_file(
                TRAVIS_INCORRECT_TIMING_TAGS_FILE
            )
        )
        self.assertEqual(2, len(self.travis_data.current_job.stages.stages))

        self.assertEqual(
            'after_script.3',
            self.travis_data.current_job.stages.stages[0]["name"]
        )
        self.assertEqual(
            '',
            self.travis_data.current_job.stages.stages[1]["name"]
        )

        # check build started and finished timestamps
        self.assertEqual(
            1408282901.278675,
            self.travis_data.current_job.stages
                .started_at["timestamp_seconds"]
        )
        self.assertEqual(
            1408282901.287937,
            self.travis_data.current_job.stages
                .finished_at["timestamp_seconds"]
        )

    def test_parse_valid_job_log_travis_sample(self):
        """Test TravisData.parse_job_log_file() with a local logfile"""
        self.travis_data.current_job.set_started_at("2014-08-17T13:40:14Z")
        # add a sample Travis CI logfile
        self.assertTrue(self.travis_data.parse_job_log_file(TRAVIS_LOG_FILE))
        self._check_travis_log()

    def test_parse_travis_log(self):
        """Test TravisData.parse_job_log() : download and parse"""
        self.travis_data.current_job.set_started_at("2014-08-17T13:40:14Z")
        # retrieve and check Travis CI logfile
        self.travis_data.parse_job_log(32774630)
        self._check_travis_log()

    def _check_travis_log(self):
        """Helper function to test parse_job_log result"""
        # checks result of parsing a sample Travis CI log file
        self.assertEqual(
            18,
            len(self.travis_data.current_job.stages.stages)
        )

        self.assertEqual(
            'git.1',
            self.travis_data.current_job.stages.stages[0]["name"]
        )
        self.assertEqual(
            '',
            self.travis_data.current_job.stages.stages[1]["name"]
        )
        self.assertEqual(
            'git.3',
            self.travis_data.current_job.stages.stages[2]["name"]
        )
        self.assertEqual(
            '',
            self.travis_data.current_job.stages.stages[3]["name"]
        )
        self.assertEqual(
            '',
            self.travis_data.current_job.stages.stages[4]["name"]
        )
        self.assertEqual(
            '',
            self.travis_data.current_job.stages.stages[5]["name"]
        )
        self.assertEqual(
            '',
            self.travis_data.current_job.stages.stages[6]["name"]
        )
        self.assertEqual(
            'install.1',
            self.travis_data.current_job.stages.stages[7]["name"]
        )
        self.assertEqual(
            'install.2',
            self.travis_data.current_job.stages.stages[8]["name"]
        )
        self.assertEqual(
            'install.3',
            self.travis_data.current_job.stages.stages[9]["name"]
        )
        self.assertEqual(
            'install.4',
            self.travis_data.current_job.stages.stages[10]["name"]
        )
        self.assertEqual(
            '',
            self.travis_data.current_job.stages.stages[11]["name"]
        )
        self.assertEqual(
            '',
            self.travis_data.current_job.stages.stages[12]["name"]
        )
        self.assertEqual(
            'after_script.1',
            self.travis_data.current_job.stages.stages[13]["name"]
        )
        self.assertEqual(
            'after_script.2',
            self.travis_data.current_job.stages.stages[14]["name"]
        )
        self.assertEqual(
            'after_script.3',
            self.travis_data.current_job.stages.stages[15]["name"]
        )
        self.assertEqual(
            'after_script.4',
            self.travis_data.current_job.stages.stages[16]["name"]
        )
        self.assertEqual(
            'after_script.5',
            self.travis_data.current_job.stages.stages[17]["name"]
        )

        # check build started and finished timestamps
        self.assertEqual(
            1408282815.329854,
            self.travis_data.current_job.stages
                .started_at["timestamp_seconds"]
        )
        self.assertEqual(
            1408282905.966106,
            self.travis_data.current_job.stages
                .finished_at["timestamp_seconds"]
        )

        # check worker tag
        self.assertDictEqual(
            {
                'hostname': 'worker-linux-12-1.bb.travis-ci.org',
                'os': 'travis-linux-11'
            },
            self.travis_data.current_job.get_property("worker")
        )

    def test_parse_travis_time_tag(self):
        """Test TravisData.parse_travis_time_tag()"""
        # read sample lines with timetags
        with open(TRAVIS_TIMING_TAGS_FILE, 'rb') as f:
            """First stage"""
            # read next log file line
            self.travis_data.parse_travis_time_tag(next(f).decode('utf-8'))

            # stage 'install.4' is started, but is not finished
            self.assertEqual(
                0,
                len(self.travis_data.current_job.stages.stages)
            )
            self.assertTrue(self.travis_data.travis_substage.has_name())
            self.assertEqual(
                'install.4',
                self.travis_data.travis_substage.get_name()
            )
            self.assertTrue(self.travis_data.travis_substage.has_timing_hash())
            self.assertTrue(self.travis_data.travis_substage.has_command())
            self.assertTrue(self.travis_data.travis_substage.has_started())
            self.assertFalse(self.travis_data.travis_substage.has_finished())

            # read next log file line
            self.travis_data.parse_travis_time_tag(next(f).decode('utf-8'))

            # stage 'install.4' is finished, and is added to Stages object
            self.assertEqual(
                1,
                len(self.travis_data.current_job.stages.stages)
            )

            self.assertEqual(
                'install.4',
                self.travis_data.current_job.stages.stages[0]["name"]
            )
            self.assertEqual(
                'CFLAGS="-O0" pip install -r requirements-tests.txt',
                self.travis_data.current_job.stages.stages[0]["command"])
            self.assertEqual(
                'install.4',
                self.travis_data.current_job.stages.stages[0]["name"]
            )
            self.assertEqual(
                1408282890.843065,
                self.travis_data.current_job.stages
                    .stages[0]["started_at"]["timestamp_seconds"]
            )
            self.assertEqual(
                1408282894.494005,
                self.travis_data.current_job.stages
                    .stages[0]["finished_at"]["timestamp_seconds"])
            self.assertEqual(
                3.650939474,
                self.travis_data.current_job.stages
                    .stages[0]["duration"]
            )

            # check build started and finished timestamps
            self.assertEqual(
                1408282890.843065,
                self.travis_data.current_job.stages
                    .started_at["timestamp_seconds"])
            self.assertEqual(
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
            self.travis_data.parse_travis_time_tag(next(f).decode('utf-8'))

            # stage 'after_script.2' is started, but is not finished
            self.assertEqual(
                1, len(self.travis_data.current_job.stages.stages)
            )
            self.assertTrue(self.travis_data.travis_substage.has_name())
            self.assertEqual(
                'after_script.2', self.travis_data.travis_substage.get_name()
            )
            self.assertTrue(self.travis_data.travis_substage.has_timing_hash())
            self.assertTrue(self.travis_data.travis_substage.has_command())
            self.assertTrue(self.travis_data.travis_substage.has_started())
            self.assertFalse(self.travis_data.travis_substage.has_finished())

            # read next log file line
            self.travis_data.parse_travis_time_tag(next(f).decode('utf-8'))

            # stage 'after_script.2' is finished,
            # and is added to Stages object
            self.assertEqual(
                2, len(self.travis_data.current_job.stages.stages))

            self.assertEqual(
                'after_script.2',
                self.travis_data.current_job.stages.stages[1]["name"])
            self.assertEqual(
                'coveralls',
                self.travis_data.current_job.stages.stages[1]["command"])
            self.assertEqual(
                1408282896.480781,
                self.travis_data.current_job.stages
                    .stages[1]["started_at"]["timestamp_seconds"])
            self.assertEqual(
                1408282901.258723,
                self.travis_data.current_job.stages
                    .stages[1]["finished_at"]["timestamp_seconds"])
            self.assertEqual(
                4.777942342,
                self.travis_data.current_job.stages.stages[1]["duration"])

            # check build started and finished timestamps
            self.assertEqual(
                1408282890.843065,
                self.travis_data.current_job.stages
                    .started_at["timestamp_seconds"])
            self.assertEqual(
                1408282901.258723,
                self.travis_data.current_job.stages
                    .finished_at["timestamp_seconds"])

            """Third stage"""
            # new TravisSubstage object was created,
            # and the next stage is started
            self.assertTrue(self.travis_data.travis_substage.has_name())
            self.assertEqual(
                'after_script.3', self.travis_data.travis_substage.get_name()
            )
            self.assertFalse(
                self.travis_data.travis_substage.has_timing_hash()
            )
            self.assertTrue(self.travis_data.travis_substage.has_command())
            self.assertTrue(self.travis_data.travis_substage.has_started())
            self.assertFalse(self.travis_data.travis_substage.has_finished())

            # read next log file line
            self.travis_data.parse_travis_time_tag(next(f).decode('utf-8'))

            # stage 'after_script.3' is finished, and is added to Stages object
            self.assertEqual(
                3, len(self.travis_data.current_job.stages.stages)
            )

            self.assertEqual(
                'after_script.3',
                self.travis_data.current_job.stages.stages[2]["name"]
            )
            self.assertEqual(
                'echo $TRAVIS_TEST_RESULT',
                self.travis_data.current_job.stages.stages[2]["command"]
            )
            self.assertFalse(
                'started_at' in self.travis_data.current_job.stages.stages[2]
            )
            self.assertFalse(
                'finished_at' in self.travis_data.current_job.stages.stages[2]
            )
            self.assertEqual(
                0, self.travis_data.current_job.stages.stages[2]["duration"])

            # check build started and finished timestamps, they don't change
            # because this stage doesn't having timing info
            self.assertEqual(
                1408282890.843065,
                self.travis_data.current_job.stages
                    .started_at["timestamp_seconds"])
            self.assertEqual(
                1408282901.258723,
                self.travis_data.current_job.stages
                    .finished_at["timestamp_seconds"])

            """Fourth stage"""
            # new TravisSubstage object was created,
            # and the next stage is started
            self.assertFalse(self.travis_data.travis_substage.has_name())
            self.assertEqual(
                'timestamp.sh Done',
                self.travis_data.travis_substage.get_name()
            )
            self.assertTrue(self.travis_data.travis_substage.has_timing_hash())
            self.assertTrue(self.travis_data.travis_substage.has_command())
            self.assertTrue(self.travis_data.travis_substage.has_started())
            self.assertFalse(self.travis_data.travis_substage.has_finished())

            # read next log file line
            self.travis_data.parse_travis_time_tag(next(f).decode('utf-8'))

            # stage 'timestamp.sh Done' is finished,
            # and is added to Stages object
            self.assertEqual(
                4, len(self.travis_data.current_job.stages.stages))

            self.assertEqual(
                '', self.travis_data.current_job.stages.stages[3]["name"])
            self.assertEqual(
                'timestamp.sh Done',
                self.travis_data.current_job.stages.stages[3]["command"])
            self.assertEqual(
                1408282901.278675,
                self.travis_data.current_job.stages
                    .stages[3]["started_at"]["timestamp_seconds"])
            self.assertEqual(
                1408282901.287937,
                self.travis_data.current_job.stages
                    .stages[3]["finished_at"]["timestamp_seconds"])
            self.assertEqual(
                0.009261320,
                self.travis_data.current_job.stages.stages[3]["duration"])

            # check build started and finished timestamps
            self.assertEqual(
                1408282890.843065,
                self.travis_data.current_job.stages
                    .started_at["timestamp_seconds"])
            self.assertEqual(
                1408282901.287937,
                self.travis_data.current_job.stages
                    .finished_at["timestamp_seconds"])

    def test_parse_travis_time_tag_incorrect(self):
        """Test TravisData.parse_travis_time_tag() with an incorrect tag"""
        # read sample lines with timetags
        with open(TRAVIS_INCORRECT_TIMING_TAGS_FILE, 'rb') as f:
            """First stage"""
            # read next log file line
            self.travis_data.parse_travis_time_tag(next(f).decode('utf-8'))

            # stage 'install.4' is started, but is not finished
            self.assertEqual(
                0, len(self.travis_data.current_job.stages.stages))
            self.assertTrue(self.travis_data.travis_substage.has_name())
            self.assertEqual(
                'install.4',
                self.travis_data.travis_substage.get_name()
            )
            self.assertTrue(self.travis_data.travis_substage.has_timing_hash())
            self.assertTrue(self.travis_data.travis_substage.has_command())
            self.assertTrue(self.travis_data.travis_substage.has_started())
            self.assertFalse(self.travis_data.travis_substage.has_finished())

            # read next log file line
            self.travis_data.parse_travis_time_tag(next(f).decode('utf-8'))

            # stage 'install.4' is not finished, end-tag is incorrect
            self.assertEqual(
                0, len(self.travis_data.current_job.stages.stages))

            # new TravisSubstage object was created
            self.assertFalse(self.travis_data.travis_substage.has_name())
            self.assertFalse(
                self.travis_data.travis_substage.has_timing_hash())
            self.assertFalse(self.travis_data.travis_substage.has_command())
            self.assertFalse(self.travis_data.travis_substage.has_started())
            self.assertFalse(self.travis_data.travis_substage.has_finished())

            # build started and finished timestamps are not set
            self.assertEqual(
                None, self.travis_data.current_job.stages.started_at)
            self.assertEqual(
                None, self.travis_data.current_job.stages.finished_at)

            """Seconds stage"""
            # read next log file line
            self.travis_data.parse_travis_time_tag(next(f).decode('utf-8'))

            # stage 'after_script.2' is started, but is not finished
            self.assertEqual(
                0, len(self.travis_data.current_job.stages.stages))
            self.assertTrue(self.travis_data.travis_substage.has_name())
            self.assertEqual(
                'after_script.2',
                self.travis_data.travis_substage.get_name()
            )
            self.assertTrue(self.travis_data.travis_substage.has_timing_hash())
            self.assertTrue(self.travis_data.travis_substage.has_command())
            self.assertTrue(self.travis_data.travis_substage.has_started())
            self.assertFalse(self.travis_data.travis_substage.has_finished())

            # read next log file line
            self.travis_data.parse_travis_time_tag(next(f).decode('utf-8'))

            # stage 'after_script.3' is not finished,
            # because timing_hash is incorrect
            self.assertEqual(
                0, len(self.travis_data.current_job.stages.stages))

            # build started and finished timestamps are not set
            self.assertEqual(
                None, self.travis_data.current_job.stages.started_at)
            self.assertEqual(
                None, self.travis_data.current_job.stages.finished_at)

            """Third stage"""
            # new TravisSubstage object was created,
            # and the next stage is started
            self.assertTrue(self.travis_data.travis_substage.has_name())
            self.assertEqual(
                'after_script.3',
                self.travis_data.travis_substage.get_name())
            self.assertFalse(
                self.travis_data.travis_substage.has_timing_hash()
            )
            self.assertTrue(self.travis_data.travis_substage.has_command())
            self.assertTrue(self.travis_data.travis_substage.has_started())
            self.assertFalse(self.travis_data.travis_substage.has_finished())

            # read next log file line
            self.travis_data.parse_travis_time_tag(next(f).decode('utf-8'))

            # stage 'after_script.3' is not finished,
            # because timing_hash is incorrect
            self.assertEqual(
                1,
                len(self.travis_data.current_job.stages.stages))

            self.assertEqual(
                'after_script.3',
                self.travis_data.current_job.stages.stages[0]["name"])
            self.assertEqual(
                'echo $TRAVIS_TEST_RESULT',
                self.travis_data.current_job.stages.stages[0]["command"])
            self.assertFalse(
                'started_at' in self.travis_data.current_job.stages.stages[0])
            self.assertFalse(
                'finished_at' in self.travis_data.current_job.stages.stages[0])
            self.assertEqual(
                0,
                self.travis_data.current_job.stages.stages[0]["duration"])

            # build started and finished timestamps are not set
            self.assertEqual(
                None, self.travis_data.current_job.stages.started_at)
            self.assertEqual(
                None, self.travis_data.current_job.stages.finished_at)

            """Fourth stage"""
            # new TravisSubstage object was created,
            # and the next stage is started
            self.assertFalse(self.travis_data.travis_substage.has_name())
            self.assertEqual(
                'timestamp.sh Done',
                self.travis_data.travis_substage.get_name())
            self.assertTrue(self.travis_data.travis_substage.has_timing_hash())
            self.assertTrue(self.travis_data.travis_substage.has_command())
            self.assertTrue(self.travis_data.travis_substage.has_started())
            self.assertFalse(self.travis_data.travis_substage.has_finished())

            # read next log file line
            self.travis_data.parse_travis_time_tag(next(f).decode('utf-8'))

            # stage 'timestamp.sh Done' is finished,
            # and is added to Stages object
            self.assertEqual(
                2, len(self.travis_data.current_job.stages.stages)
            )

            self.assertEqual(
                '', self.travis_data.current_job.stages.stages[1]["name"]
            )
            self.assertEqual(
                'timestamp.sh Done',
                self.travis_data.current_job.stages.stages[1]["command"])
            self.assertEqual(
                1408282901.278675,
                self.travis_data.current_job.stages
                    .stages[1]["started_at"]["timestamp_seconds"])
            self.assertEqual(
                1408282901.287937,
                self.travis_data.current_job.stages
                    .stages[1]["finished_at"]["timestamp_seconds"])
            self.assertEqual(
                0.009261320,
                self.travis_data.current_job.stages.stages[1]["duration"])

            # check build started and finished timestamps
            self.assertEqual(
                1408282901.278675,
                self.travis_data.current_job.stages
                    .started_at["timestamp_seconds"])
            self.assertEqual(
                1408282901.287937,
                self.travis_data.current_job.stages
                    .finished_at["timestamp_seconds"])

    def test_parse_travis_worker_tag(self):
        """Test TravisData.parse_travis_worker_tag()"""
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
        Test TravisData.has_timing_tags()

        This should be true if build was
        started at 2014-07-30 or after.
        """
        self.assertFalse(self.travis_data.has_timing_tags())

        self.travis_data.current_job.set_started_at("2014-07-29T16:30:00Z")
        self.assertFalse(self.travis_data.has_timing_tags())

        self.travis_data.current_job.set_started_at("2014-08-07T16:30:00Z")
        self.assertTrue(self.travis_data.has_timing_tags())

    def test_get_job_duration(self):
        """
        Test job duration calculation.
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
        self.travis_data.current_job = BuildJob()
        self.travis_data.current_job.set_finished_at(
            "2014-07-30T16:31:00.123Z"
        )
        self.assertAlmostEqual(0.0, self.travis_data.get_job_duration(), 0)
