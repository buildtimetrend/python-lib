# vim: set expandtab sw=4 ts=4:
'''
Manages settings of buildtime trend

Copyright (C) 2014 Dieter Adriaenssens <ruleant@users.sourceforge.net>

This file is part of buildtime-trend
<https://github.com/ruleant/buildtime-trend/>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

import os
import buildtimetrend
from buildtimetrend.collection import Collection


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
            self.set_project_name(buildtimetrend.NAME)

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
            project_name = self.get_setting("project_name")

            # use Travis repo slug as project name
            if 'TRAVIS_REPO_SLUG' in os.environ:
                project_name = os.getenv('TRAVIS_REPO_SLUG')

            return project_name

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
