# vim: set expandtab sw=4 ts=4:
#
# Unit tests for Travis env_var related functions
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
from buildtimetrend.settings import Settings
from buildtimetrend.travis import env_var
import unittest


class TestTravisEnvVar(unittest.TestCase):

    """Unit tests for Travis CI env var loading functions"""

    def setUp(self):
        """Initialise test environment before each test."""
        # reinit settings singleton
        Settings().__init__()

    def test_load_travis_env_vars(self):
        """Test load_travis_env_vars"""
        settings = Settings()

        self.assertEqual(None, settings.get_setting("ci_platform"))
        self.assertEqual(None, settings.get_setting("build"))
        self.assertEqual(None, settings.get_setting("job"))
        self.assertEqual(None, settings.get_setting("branch"))
        self.assertEqual(None, settings.get_setting("result"))
        self.assertEqual(None, settings.get_setting("build_trigger"))
        self.assertEqual(None, settings.get_setting("pull_request"))
        self.assertEqual(buildtimetrend.NAME, settings.get_project_name())

        #setup Travis env vars
        if "TRAVIS" in os.environ and os.environ["TRAVIS"] == "true":
            reset_travis_vars = False
            expected_build = os.environ["TRAVIS_BUILD_NUMBER"]
            expected_job = os.environ["TRAVIS_JOB_NUMBER"]
            expected_branch = os.environ["TRAVIS_BRANCH"]
            expected_project_name = os.environ["TRAVIS_REPO_SLUG"]
            copy_pull_request = os.environ["TRAVIS_PULL_REQUEST"]
        else:
            reset_travis_vars = True
            os.environ["TRAVIS"] = "true"
            expected_build = os.environ["TRAVIS_BUILD_NUMBER"] = "123"
            expected_job = os.environ["TRAVIS_JOB_NUMBER"] = "123.1"
            expected_branch = os.environ["TRAVIS_BRANCH"] = "branch1"
            expected_project_name = \
                os.environ["TRAVIS_REPO_SLUG"] = "test/project"

        # setup Travis test result
        if "TRAVIS_TEST_RESULT" in os.environ:
            reset_travis_result = False
            copy_result = os.environ["TRAVIS_TEST_RESULT"]
        else:
            reset_travis_result = True

        os.environ["TRAVIS_TEST_RESULT"] = "0"
        os.environ["TRAVIS_PULL_REQUEST"] = "false"

        env_var.load_all(settings)

        self.assertEqual("travis", settings.get_setting("ci_platform"))
        self.assertEqual(expected_build, settings.get_setting("build"))
        self.assertEqual(expected_job, settings.get_setting("job"))
        self.assertEqual(expected_branch, settings.get_setting("branch"))
        self.assertEqual(expected_project_name, settings.get_project_name())
        self.assertEqual("passed", settings.get_setting("result"))
        self.assertEqual("push", settings.get_setting("build_trigger"))
        self.assertDictEqual(
            {
                'is_pull_request': False,
                'title': None,
                'number': None
            },
            settings.get_setting("pull_request")
        )

        os.environ["TRAVIS_TEST_RESULT"] = "1"
        # build is a pull request
        expected_pull_request = os.environ["TRAVIS_PULL_REQUEST"] = "123"
        env_var.load_all()
        self.assertEqual("failed", settings.get_setting("result"))
        self.assertEqual(
            "pull_request", settings.get_setting("build_trigger")
        )
        self.assertDictEqual(
            {
                'is_pull_request': True,
                'title': "unknown",
                'number': expected_pull_request
            },
            settings.get_setting("pull_request")
        )

        # build is not a pull request
        os.environ["TRAVIS_PULL_REQUEST"] = "false"
        env_var.load_all(settings)
        self.assertEqual("push", settings.get_setting("build_trigger"))
        self.assertDictEqual(
            {
                'is_pull_request': False,
                'title': None,
                'number': None
            },
            settings.get_setting("pull_request")
        )

        # reset test Travis vars
        if reset_travis_vars:
            del os.environ["TRAVIS"]
            del os.environ["TRAVIS_BUILD_NUMBER"]
            del os.environ["TRAVIS_JOB_NUMBER"]
            del os.environ["TRAVIS_BRANCH"]
            del os.environ["TRAVIS_REPO_SLUG"]
            del os.environ["TRAVIS_PULL_REQUEST"]
        else:
            os.environ["TRAVIS_PULL_REQUEST"] = copy_pull_request

        # reset Travis test result
        if reset_travis_result:
            del os.environ["TRAVIS_TEST_RESULT"]
        else:
            os.environ["TRAVIS_TEST_RESULT"] = copy_result

    def test_load_build_matrix_env_vars(self):
        """Test load_build_matrix_env_vars"""
        settings = Settings()

        self.assertEqual(None, settings.get_setting("build_matrix"))

        #setup Travis env vars
        if "TRAVIS" in os.environ and os.environ["TRAVIS"] == "true":
            reset_travis_vars = False
            expected_os = os.environ["TRAVIS_OS_NAME"]
            copy_python = os.environ["TRAVIS_PYTHON_VERSION"]
            del os.environ["TRAVIS_PYTHON_VERSION"]
        else:
            reset_travis_vars = True
            os.environ["TRAVIS"] = "true"
            expected_os = os.environ["TRAVIS_OS_NAME"] = "test_os"

        # temporarily remove PYTHON VERSION
        if "TRAVIS_PYTHON_VERSION" in os.environ:
            reset_python_version = True
            copy_python = os.environ["TRAVIS_PYTHON_VERSION"]
            del os.environ["TRAVIS_PYTHON_VERSION"]
        else:
            reset_python_version = False

        # test language and language versions
        test_languages = [
            {
                'env_var': 'TRAVIS_DART_VERSION',
                'language': 'dart',
                'test_value': "1.1"
            },
            {
                'env_var': 'TRAVIS_GO_VERSION',
                'language': 'go',
                'test_value': "1.2"
            },
            {
                'env_var': 'TRAVIS_HAXE_VERSION',
                'language': 'haxe',
                'test_value': "1.3"
            },
            {
                'env_var': 'TRAVIS_JDK_VERSION',
                'language': 'java',
                'test_value': "1.4"
            },
            {
                'env_var': 'TRAVIS_JULIA_VERSION',
                'language': 'julia',
                'test_value': "1.5"
            },
            {
                'env_var': 'TRAVIS_NODE_VERSION',
                'language': 'javascript',
                'test_value': "1.6"
            },
            {
                'env_var': 'TRAVIS_OTP_RELEASE',
                'language': 'erlang',
                'test_value': "1.7"
            },
            {
                'env_var': 'TRAVIS_PERL_VERSION',
                'language': 'perl',
                'test_value': "1.8"
            },
            {
                'env_var': 'TRAVIS_PHP_VERSION',
                'language': 'php',
                'test_value': "1.9"
            },
            {
                'env_var': 'TRAVIS_PYTHON_VERSION',
                'language': 'python',
                'test_value': "1.10"
            },
            {
                'env_var': 'TRAVIS_R_VERSION',
                'language': 'r',
                'test_value': "1.11"
            },
            {
                'env_var': 'TRAVIS_RUBY_VERSION',
                'language': 'ruby',
                'test_value': "1.12"
            },
            {
                'env_var': 'TRAVIS_RUST_VERSION',
                'language': 'rust',
                'test_value': "1.13"
            },
            {
                'env_var': 'TRAVIS_SCALA_VERSION',
                'language': 'scala',
                'test_value': "1.14"
            }
        ]

        # test languages
        for language in test_languages:
            if language['env_var'] in os.environ:
                reset_travis_lang_version = False
                expected_lang_version = os.environ[language['env_var']]
            else:
                reset_travis_lang_version = True
                expected_lang_version = \
                    os.environ[language['env_var']] = language['test_value']

            env_var.load_build_matrix_env_vars(settings)

            self.assertDictEqual(
                {
                    'os': expected_os,
                    'language': language['language'],
                    'language_version': expected_lang_version,
                    'summary': "%s %s %s" % (
                        language['language'],
                        expected_lang_version,
                        expected_os
                    )
                },
                settings.get_setting("build_matrix")
            )

            # reset Travis test result
            if reset_travis_lang_version:
                del os.environ[language['env_var']]

        # reset test Travis vars
        if reset_travis_vars:
            del os.environ["TRAVIS"]
            del os.environ["TRAVIS_OS_NAME"]

        # reset removed python version
        if reset_python_version:
            os.environ["TRAVIS_PYTHON_VERSION"] = copy_python

    def test_load_build_matrix_env_vars_parameters(self):
        """Test load_travis_env_vars, optional parameters"""
        # setup Travis env vars
        if "TRAVIS" in os.environ and os.environ["TRAVIS"] == "true":
            reset_travis_vars = False
            copy_os = os.environ["TRAVIS_OS_NAME"]
        else:
            reset_travis_vars = True
            os.environ["TRAVIS"] = "true"

        # temporarily remove OS VERSION
        if "TRAVIS_OS_NAME" in os.environ:
            reset_os = True
            copy_os = os.environ["TRAVIS_OS_NAME"]
            del os.environ["TRAVIS_OS_NAME"]
        else:
            reset_os = False

        # temporarily remove PYTHON VERSION
        if "TRAVIS_PYTHON_VERSION" in os.environ:
            reset_python_version = True
            copy_python = os.environ["TRAVIS_PYTHON_VERSION"]
            del os.environ["TRAVIS_PYTHON_VERSION"]
        else:
            reset_python_version = False

        # test optional build matrix parameters
        test_parameters = [
            {
                'env_var': 'TRAVIS_XCODE_SDK',
                'parameter': 'xcode_sdk',
                'test_value': "test_x_sdk"
            },
            {
                'env_var': 'TRAVIS_XCODE_SCHEME',
                'parameter': 'xcode_scheme',
                'test_value': "test_x_scheme"
            },
            {
                'env_var': 'TRAVIS_XCODE_PROJECT',
                'parameter': 'xcode_project',
                'test_value': "test_x_project"
            },
            {
                'env_var': 'TRAVIS_XCODE_WORKSPACE',
                'parameter': 'xcode_workspace',
                'test_value': "test_x_workspace"
            },
            {
                'env_var': 'CC',
                'parameter': 'compiler',
                'test_value': "test_gcc"
            },
            {
                'env_var': 'ENV',
                'parameter': 'parameters',
                'test_value': "test_env"
            }
        ]

        # test parameters
        for parameter in test_parameters:
            Settings().__init__()
            settings = Settings()

            if parameter['env_var'] in os.environ:
                reset_travis_parameter = False
                expected_param_value = os.environ[parameter['env_var']]
            else:
                reset_travis_parameter = True
                expected_param_value = os.environ[parameter['env_var']] = \
                    parameter['test_value']

            env_var.load_build_matrix_env_vars(settings)

            self.assertDictEqual(
                {
                    parameter["parameter"]: expected_param_value,
                    'summary': expected_param_value
                },
                settings.get_setting("build_matrix")
            )

            # reset Travis parameters
            if reset_travis_parameter:
                del os.environ[parameter['env_var']]

        # reset test Travis vars
        if reset_travis_vars:
            del os.environ["TRAVIS"]

        # reset removed os name
        if reset_os:
            os.environ["TRAVIS_OS_NAME"] = copy_os

        # reset removed python version
        if reset_python_version:
            os.environ["TRAVIS_PYTHON_VERSION"] = copy_python
