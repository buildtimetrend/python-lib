# vim: set expandtab sw=4 ts=4:
'''
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
from dateutil.parser import parse
from buildtimetrend.settings import get_project_info


def format_timestamp(timestamp):
    '''
    Format a datetime timestamp (UTC) to ISO format (YYYY-MM-DDTHH:MM:SS)

    Parameters :
    - timestamp : timestamp, seconds since epoch
    '''
    timestamp_datetime = datetime.utcfromtimestamp(timestamp)
    return timestamp_datetime.isoformat()


def split_timestamp(timestamp):
    '''
    Split a timestamp in seconds since epoch in all seperate components :
      year, month, day of month, day of week,
      hour (12 and 24 hour), minute, second

    Parameters :
    - timestamp : timestamp, seconds since epoch
    '''
    return split_datetime(datetime.utcfromtimestamp(timestamp))


def split_isotimestamp(isotimestamp):
    '''
    Split a timestamp in isoformat in all seperate components :
      year, month, day of month, day of week,
      hour (12 and 24 hour), minute, second

    Parameters :
    - isotimestamp : timestamp in isoformat YYYY-MM-DDTHH:MM:SS
    '''
    # use dateutil.parser.parse to pare the timestamp
    return split_datetime(parse(isotimestamp))


def split_datetime(timestamp_datetime):
    '''
    Split a timestamp in datetime format in all seperate components :
      year, month, day of month, day of week,
      hour (12 and 24 hour), minute, second

    Parameters :
    - timestamp_datetime : timestamp in datetime class format
    '''
    timestamp_dict = {}
    timestamp_dict["timestamp"] = timestamp_datetime.isoformat()
    timestamp_dict["year"] = timestamp_datetime.strftime("%Y")
    timestamp_dict["month"] = timestamp_datetime.strftime("%m")
    timestamp_dict["month_short_en"] = timestamp_datetime.strftime("%b")
    timestamp_dict["month_full_en"] = timestamp_datetime.strftime("%B")
    timestamp_dict["day_of_month"] = timestamp_datetime.strftime("%d")
    timestamp_dict["day_of_week"] = timestamp_datetime.strftime("%w")
    timestamp_dict["day_of_week_short_en"] = timestamp_datetime.strftime("%a")
    timestamp_dict["day_of_week_full_en"] = timestamp_datetime.strftime("%A")
    timestamp_dict["hour_12"] = timestamp_datetime.strftime("%I")
    timestamp_dict["hour_ampm"] = timestamp_datetime.strftime("%p")
    timestamp_dict["hour_24"] = timestamp_datetime.strftime("%H")
    timestamp_dict["minute"] = timestamp_datetime.strftime("%M")
    timestamp_dict["second"] = timestamp_datetime.strftime("%S")

    return timestamp_dict


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


def check_file(filename):
    '''
    Checks if a file exists.

    Parameters :
    - filename : file to be checked
    Returns false if file doesn't exist, true if it exists.
    '''
    # load timestamps file
    if not os.path.isfile(filename):
        print 'File doesn\'t exist : {0}'.format(filename)
        return False

    return True