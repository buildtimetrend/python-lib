# vim: set expandtab sw=4 ts=4:
# pylint: disable=invalid-name,too-few-public-methods
"""
Manage Buildtime Trend settings.

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

import os
import getopt
import yaml
import keen
import buildtimetrend
from buildtimetrend.collection import Collection
from buildtimetrend.tools import check_file
from buildtimetrend.tools import set_loglevel
from buildtimetrend.tools import get_logger


class Settings(object):

    """
    Settings class is a singleton.

    Inspired by
    http://python-3-patterns-idioms-test.readthedocs.org/ \
    en/latest/Singleton.html
    """

    class __Settings(object):

        """ Settings class contains settings and config options. """

        def __init__(self):
            """ Initialise class. """
            self.settings = Collection()

            # set loglevel
            self.add_setting("loglevel", "WARNING")

            # set default project name
            self.set_project_name(buildtimetrend.NAME)

            # set modes
            self.set_mode("native", False)
            self.set_mode("keen", True)

            # set default paths
            self.add_setting('dashboard_configfile',
                             'dashboard/config.js')

        def set_project_name(self, name):
            """
            Set project name.

            Parameters :
            - name : project name
            """
            self.add_setting("project_name", name)

        def get_project_name(self):
            """ Get project name. """
            return self.get_setting("project_name")

        def set_client(self, name, version):
            """
            Set client name and version.

            Parameters :
            - name : client name (fe. service, python-client)
            - version : client version
            """
            self.add_setting("client", name)
            self.add_setting("client_version", version)

        def add_setting(self, name, value):
            """
            Add a setting.

            Parameters :
            - name : Setting name
            - value : Setting value
            """
            self.settings.add_item(name, value)

        def get_setting(self, name):
            """
            Get a setting value.

            Parameters :
            - name : Setting name
            """
            return self.settings.get_item(name)

        def load_settings(self, argv=None, config_file="config.yml"):
            """
            Load config settings.

            Settings are retrieved from :
            - configfile
            - environment variables
            - command line arguments
            """
            self.load_config_file(config_file)
            self.load_env_vars()
            return self.process_argv(argv)

        def load_config_file(self, config_file):
            """
            Load settings from a config file.

            Parameters :
            - config_file : name of the config file
            """
            if not check_file(config_file):
                return False

            with open(config_file, 'r') as file_stream:
                config = yaml.load(file_stream)
                self.settings.add_items(config["buildtimetrend"])

                set_loglevel(self.get_setting("loglevel"))

                # set Keen.io settings
                if "keen" in config:
                    if "project_id" in config["keen"]:
                        keen.project_id = config["keen"]["project_id"]
                    if "write_key" in config["keen"]:
                        keen.write_key = config["keen"]["write_key"]
                    if "read_key" in config["keen"]:
                        keen.read_key = config["keen"]["read_key"]
                    if "master_key" in config["keen"]:
                        keen.master_key = config["keen"]["master_key"]
                return True

        def get_project_info(self):
            """ Get project info as a dictonary. """
            return {
                "lib_version": buildtimetrend.VERSION,
                "schema_version": buildtimetrend.SCHEMA_VERSION,
                "client": str(self.get_setting("client")),
                "client_version": str(self.get_setting("client_version")),
                "project_name": str(self.get_project_name())
            }

        def process_argv(self, argv):
            """
            Process command line arguments.

            Returns a list with arguments (non-options) or
            None if options are invalid
            """
            if argv is None:
                return None

            usage_string = '%s -h --log=<log_level> --build=<buildID>' \
                ' --job=<jobID> --branch=<branchname> --repo=<repo_slug>' \
                ' --ci=<ci_platform> --result=<build_result>' \
                ' --mode=<storage_mode>' % \
                argv[0]

            options = {
                "--build": "build",
                "--job": "job",
                "--branch": "branch",
                "--ci": "ci_platform",
                "--result": "result"
            }

            try:
                opts, args = getopt.getopt(
                    argv[1:], "h", [
                        "log=",
                        "build=", "job=", "branch=", "repo=",
                        "ci=", "result=", "mode=", "help"]
                )
            except getopt.GetoptError:
                print(usage_string)
                return None

            # check options
            for opt, arg in opts:
                if opt in ('-h', "--help"):
                    print(usage_string)
                    return None
                elif opt == "--log":
                    set_loglevel(arg)
                elif opt in options:
                    self.add_setting(options[opt], arg)
                elif opt == "--repo":
                    self.set_project_name(arg)
                elif opt == "--mode":
                    self.set_mode(arg)

            return args

        def set_mode(self, mode, value=True):
            """
            Set operating mode.

            Parameters:
            - mode : keen, native
            - value : enable (=True, default) or disable (=False) mode
            """
            if mode == "native":
                self.add_setting("mode_native", bool(value))
            elif mode == "keen":
                self.add_setting("mode_keen", bool(value))

        def load_env_vars(self):
            """
            Load environment variables.

            Assign the environment variable values to
            the corresponding setting.
            """
            # assign environment variable values to setting value
            if self.env_var_to_settings("BTT_LOGLEVEL", "loglevel"):
                set_loglevel(self.get_setting("loglevel"))

            self.env_var_to_settings("TRAVIS_ACCOUNT_TOKEN",
                                     "travis_account_token")
            self.env_var_to_settings("BUILD_TREND_CONFIGFILE",
                                     "dashboard_configfile")

        def env_var_to_settings(self, env_var_name, settings_name):
            """
            Store environment variable value as a setting.

            Parameters:
            - env_var_name : Name of the environment variable
            - settings_name : Name of the corresponding settings value
            """
            logger = get_logger()

            if env_var_name in os.environ:
                self.add_setting(settings_name, os.environ[env_var_name])
                logger.debug(
                    "Setting %s was set to %s",
                    settings_name, os.environ[env_var_name])
                return True
            else:
                logger.debug(
                    "Setting %s was not set,"
                    " environment variable %s doesn't exist",
                    settings_name, env_var_name)
                return False

    instance = None

    def __new__(cls):  # __new__ always a classmethod
        """ Create a singleton. """
        if not Settings.instance:
            Settings.instance = Settings.__Settings()
        return Settings.instance

    def __getattr__(self, name):
        """ Redirect access to get singleton properties. """
        return getattr(self.instance, name)

    def __setattr__(self, name):
        """ Redirect access to set singleton properties. """
        return setattr(self.instance, name)
