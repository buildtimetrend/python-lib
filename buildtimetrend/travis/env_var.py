# vim: set expandtab sw=4 ts=4:
"""
Travis CI environment variable loading functions.

Copyright (C) 2014-2015 Dieter Adriaenssens <ruleant@users.sourceforge.net>

This file is part of buildtimetrend/python-lib
<https://github.com/buildtimetrend/python-lib/>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
from builtins import str
from builtins import object
import os
from buildtimetrend.settings import Settings
from buildtimetrend.collection import Collection
from buildtimetrend.travis import convert_build_result


def load_travis_env_vars():
    """
    Load Travis CI environment variables.

    Load Travis CI environment variables and assign their values to
    the corresponding setting value.
    """
    if "TRAVIS" in os.environ and os.environ["TRAVIS"] == "true":
        settings = Settings()

        # set ci_platform setting to "travis"
        settings.add_setting("ci_platform", "travis")

        # assign TRAVIS environment variable values to setting value
        settings.env_var_to_settings("TRAVIS_BUILD_NUMBER", "build")
        settings.env_var_to_settings("TRAVIS_JOB_NUMBER", "job")
        settings.env_var_to_settings("TRAVIS_BRANCH", "branch")
        settings.env_var_to_settings("TRAVIS_REPO_SLUG", "project_name")

        # convert and set Travis build result
        if "TRAVIS_TEST_RESULT" in os.environ:
            # map $TRAVIS_TEST_RESULT to a more readable value
            settings.add_setting(
                "result",
                convert_build_result(os.environ["TRAVIS_TEST_RESULT"])
            )

        load_build_matrix_env_vars(settings)
        load_travis_pr_env_vars(settings)


def load_build_matrix_env_vars(settings):
    """
    Retrieve build matrix data from environment variables.

    Load Travis CI build matrix environment variables
    and assign their values to the corresponding setting value.

    Properties :
    - language
    - language version (if applicable)
    - compiler (if applicable)
    - operating system
    - environment parameters

    Parameters:
    - settings: Settings instance
    """
    if "TRAVIS" in os.environ and os.environ["TRAVIS"] == "true":
        build_matrix = Collection()

        if "TRAVIS_OS_NAME" in os.environ:
            build_matrix.add_item("os", os.environ["TRAVIS_OS_NAME"])

        # set language and language version
        language_env_vars = {
            'TRAVIS_DART_VERSION': 'dart',
            'TRAVIS_GO_VERSION': 'go',
            'TRAVIS_HAXE_VERSION': 'haxe',
            'TRAVIS_JDK_VERSION': 'java',
            'TRAVIS_JULIA_VERSION': 'julia',
            'TRAVIS_NODE_VERSION': 'javascript',
            'TRAVIS_OTP_RELEASE': 'erlang',
            'TRAVIS_PERL_VERSION': 'perl',
            'TRAVIS_PHP_VERSION': 'php',
            'TRAVIS_PYTHON_VERSION': 'python',
            'TRAVIS_R_VERSION': 'r',
            'TRAVIS_RUBY_VERSION': 'ruby',
            'TRAVIS_RUST_VERSION': 'rust',
            'TRAVIS_SCALA_VERSION': 'scala'
        }
        for env_var, language in language_env_vars.items():
            if env_var in os.environ:
                build_matrix.add_item("language", language)
                build_matrix.add_item(
                    "language_version",
                    str(os.environ[env_var])
                )

        # language specific build matrix parameters
        parameters = {
            'TRAVIS_XCODE_SDK': 'xcode_sdk',  # Objective-C
            'TRAVIS_XCODE_SCHEME': 'xcode_scheme',  # Objective-C
            'TRAVIS_XCODE_PROJECT': 'xcode_project',  # Objective-C
            'TRAVIS_XCODE_WORKSPACE': 'xcode_workspace',  # Objective-C
            'CC': 'compiler',  # C, C++
            'ENV': 'parameters'
        }

        for parameter, name in parameters.items():
            if parameter in os.environ:
                build_matrix.add_item(name, str(os.environ[parameter]))

        settings.add_setting(
            "build_matrix",
            build_matrix.get_items_with_summary()
        )


def load_travis_pr_env_vars(settings):
    """
    Load Travis CI pull request environment variables.

    Load Travis CI pull request environment variables
    and assign their values to the corresponding setting value.
    """
    if "TRAVIS" in os.environ and os.environ["TRAVIS"] == "true" and \
            "TRAVIS_PULL_REQUEST" in os.environ and \
            not os.environ["TRAVIS_PULL_REQUEST"] == "false":
        settings.add_setting("build_trigger", "pull_request")
        settings.add_setting(
            "pull_request",
            {
                'is_pull_request': True,
                'title': "unknown",
                'number': os.environ["TRAVIS_PULL_REQUEST"]
            }
        )
    else:
        settings.add_setting("build_trigger", "push")
        settings.add_setting(
            "pull_request",
            {
                'is_pull_request': False,
                'title': None,
                'number': None
            }
        )
