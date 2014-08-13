'''
vim: set expandtab sw=4 ts=4:

Collection of tool functions

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

import copy
import os
from datetime import datetime


def format_timestamp(timestamp):
    '''
    Format a datetime timestamp (UTC) to ISO format (YYYY-MM-DDTHH:MM:SS)

    Parameters :
    - timestamp : timestamp, seconds since epoch
    '''
    timestamp_datetime = datetime.utcfromtimestamp(timestamp)
    return timestamp_datetime.isoformat()


def split_isotimestamp(isotimestamp):
    '''
    Split a timestamp in isoformat in all seperate components :
      year, month, day of month, day of week,
      hour (12 and 24 hour), minute, second
    '''
    timestamp_datetime = datetime.strptime(isotimestamp, "%Y-%m-%dT%H:%M:%S")

    timestamp_dict = {}
    timestamp_dict["timestamp"] = timestamp_datetime.isoformat()
    timestamp_dict["year"] = timestamp_datetime.strftime("%Y")
    timestamp_dict["month"] = timestamp_datetime.strftime("%m")
    timestamp_dict["day_of_month"] = timestamp_datetime.strftime("%d")
    timestamp_dict["day_of_week"] = timestamp_datetime.strftime("%w")
    timestamp_dict["hour_12"] = timestamp_datetime.strftime("%I")
    timestamp_dict["hour_ampm"] = timestamp_datetime.strftime("%p")
    timestamp_dict["hour_24"] = timestamp_datetime.strftime("%H")
    timestamp_dict["minute"] = timestamp_datetime.strftime("%M")
    timestamp_dict["second"] = timestamp_datetime.strftime("%S")

    return timestamp_dict


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
    # TODO get version and schema_version from Config
    version = "0.2-dev"
    schema_version = "1"
    project_name = str(get_project_name())

    return {
        "version": version,
        "schema_version": schema_version,
        "project_name": project_name
    }


def add_project_info_dict(payload):
    '''
    Adds project info to a dictonary
    Param payload: dictonary payload
    '''
    if payload is None and type(payload) is not dict:
        raise TypeError("param payload should be a dictionary")

    payload_as_dict = copy.deepcopy(payload)

    payload_as_dict["buildtime_trend"] = get_project_info()

    return payload_as_dict


def add_project_info_list(payload):
    '''
    Adds project info to a list of dictionaries
    Param payload: list of dictionaries
    '''
    if payload is None and type(payload) is not list:
        raise TypeError("param payload should be a list")

    payload_as_list = []

    # loop over dicts in payload and add project info to each one
    for event_dict in payload:
        payload_as_list.append(add_project_info_dict(event_dict))

    return payload_as_list
