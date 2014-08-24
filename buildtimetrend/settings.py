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

VERSION = "0.2-dev"
SCHEMA_VERSION = "2"


def get_project_name():
    '''
    Get project name
    '''

    # use Travis repo slug as project name
    if 'TRAVIS_REPO_SLUG' in os.environ:
        return os.getenv('TRAVIS_REPO_SLUG')

    return "None"


def get_project_info():
    '''
    Get project info as a dictonary
    '''
    project_name = str(get_project_name())

    return {
        "version": VERSION,
        "schema_version": SCHEMA_VERSION,
        "project_name": str(get_project_name())
    }
