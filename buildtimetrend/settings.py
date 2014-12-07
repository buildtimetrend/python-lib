# vim: set expandtab sw=4 ts=4:
# pylint: disable=invalid-name,too-few-public-methods
'''
Manages settings of buildtime trend

Copyright (C) 2014 Dieter Adriaenssens <ruleant@users.sourceforge.net>

This file is part of buildtime-trend
<https://github.com/ruleant/buildtime-trend/>

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
'''

import sys
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
    '''
    Settings class is a singleton
    Inspired by
 http://python-3-patterns-idioms-test.readthedocs.org/en/latest/Singleton.html
    '''
    class __Settings(object):
        '''
        Settings class contains settings and config options
        '''
        def __init__(self):
            '''
            Initialise class
            '''
            self.settings = Collection()

            # set default project name
            self.set_project_name(buildtimetrend.NAME)

            # set modes
            self.add_setting("mode_native", False)
            self.add_setting("mode_keen", True)

        def set_project_name(self, name):
            '''
            Set project name
            Parameters :
            - name : project name
            '''
            self.add_setting("project_name", name)

        def get_project_name(self):
            '''
            Get project name
            '''
            return self.get_setting("project_name")

        def add_setting(self, name, value):
            '''
            Add a setting

            Parameters :
            - name : Setting name
            - value : Setting value
            '''
            self.settings.add_item(name, value)

        def get_setting(self, name):
            '''
            Get a setting value

            Parameters :
            - name : Setting name
            '''
            return self.settings.get_item(name)

        def load_config_file(self, config_file):
            '''
            Load settings from a config file

            Parameters :
            - config_file : name of the config file
            '''
            if not check_file(config_file):
                return False

            with open(config_file, 'rb') as file_stream:
                config = yaml.load(file_stream)
                self.settings.add_items(config["buildtimetrend"])

                # set Keen.io settings
                if "keen" in config:
                    if "project_id" in config["keen"]:
                        keen.project_id = config["keen"]["project_id"]
                    if "write_key" in config["keen"]:
                        keen.write_key = config["keen"]["write_key"]
                    if "read_key" in config["keen"]:
                        keen.read_key = config["keen"]["read_key"]
                return True

        def get_project_info(self):
            '''
            Get project info as a dictonary
            '''
            return {
                "version": buildtimetrend.VERSION,
                "schema_version": buildtimetrend.SCHEMA_VERSION,
                "project_name": str(self.get_project_name())
            }

    instance = None

    def __new__(cls):  # __new__ always a classmethod
        ''' Create a singleton '''
        if not Settings.instance:
            Settings.instance = Settings.__Settings()
        return Settings.instance

    def __getattr__(self, name):
        ''' Redirect access to get singleton properties '''
        return getattr(self.instance, name)

    def __setattr__(self, name):
        ''' Redirect access to set singleton properties '''
        return setattr(self.instance, name)


def process_argv(argv):
    '''
    Process command line arguments
    '''
    usage_string = '%s -h --log=<log_level> --build=<buildID>' \
        ' --job=<jobID> --branch=<branchname> --repo=<repo_slug>' \
        ' --ci=<ci_platform> --result=<build_result> --mode=<storage_mode>' % \
        argv[0]

    settings = Settings()

    try:
        opts, args = getopt.getopt(
            argv[1:], "h", [
                "log=",
                "build=", "job=", "branch=", "repo=",
                "ci=", "result=", "mode=", "help"]
        )
    except getopt.GetoptError:
        print usage_string
        sys.exit(2)

    # check options
    for opt, arg in opts:
        if opt in ('-h', "--help"):
            print usage_string
            sys.exit()
        elif opt == "--log":
            set_loglevel(arg)
        elif opt == "--build":
            settings.add_setting("build", arg)
        elif opt == "--job":
            settings.add_setting("job", arg)
        elif opt == "--branch":
            settings.add_setting("branch", arg)
        elif opt == "--repo":
            settings.set_project_name(arg)
        elif opt == "--ci":
            settings.add_setting("ci_platform", arg)
        elif opt == "--result":
            settings.add_setting("result", arg)
        elif opt == "--mode":
            if arg == "native":
                settings.add_setting("mode_native", True)
            elif arg == "keen":
                settings.add_setting("mode_keen", True)

    return args


def env_var_to_settings(env_var_name, settings_name):
    '''
    Store environment variable value as a setting
    Parameters:
    - env_var_name : Name of the environment variable
    - settings_name : Name of the corresponding settings value
    '''
    logger = get_logger()

    if env_var_name in os.environ:
        Settings().add_setting(settings_name, os.environ[env_var_name])
        logger.debug(
            "Setting %s was set to %s",
            settings_name, os.environ[env_var_name])
        return True
    else:
        logger.debug(
            "Setting %s was not set, environment variable %s doesn't exist",
            settings_name, env_var_name)
        return False
