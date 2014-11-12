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

import os
import logging
import buildtimetrend
from datetime import datetime
from dateutil.parser import parse
from dateutil.tz import tzutc


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
    dt_utc = datetime.utcfromtimestamp(timestamp).replace(tzinfo=tzutc())
    return split_datetime(dt_utc)


def split_isotimestamp(isotimestamp):
    '''
    Split a timestamp in isoformat in all seperate components :
      year, month, day of month, day of week,
      hour (12 and 24 hour), minute, second

    Parameters :
    - isotimestamp : timestamp in isoformat YYYY-MM-DDTHH:MM:SS
    '''
    # use dateutil.parser.parse to parse the timestamp
    return split_datetime(parse(isotimestamp, tzinfos={"UTC": +0}))


def split_datetime(timestamp_datetime):
    '''
    Split a timestamp in datetime format in all seperate components :
      year, month, day of month, day of week,
      hour (12 and 24 hour), minute, second

    Parameters :

    - timestamp_datetime : timestamp in datetime class format
    '''
    if timestamp_datetime is None or type(timestamp_datetime) is not datetime:
        raise TypeError("param %s should be a datetime instance" %
                        'timestamp_datetime')

    timestamp_dict = {}
    timestamp_dict["isotimestamp"] = timestamp_datetime.isoformat()

    # epoch = 1 Jan 1970
    epoch = datetime.utcfromtimestamp(0)
    # add timezone info to epoch if timestamp is timezone aware
    if timestamp_datetime.tzname() is not None:
        epoch = datetime.utcfromtimestamp(0).replace(tzinfo=tzutc())

    # seconds since epoch
    timestamp_dict["timestamp_seconds"] = \
        (timestamp_datetime - epoch).total_seconds()

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
    timestamp_dict["microsecond"] = timestamp_datetime.strftime("%f")
    timestamp_dict["timezone"] = timestamp_datetime.strftime("%Z")
    timestamp_dict["timezone_offset"] = timestamp_datetime.strftime("%z")

    return timestamp_dict


def nano2sec(time):
    '''
    Convert time in nanoseconds to seconds
    Param time nanoseconds
    '''
    return float(time) / float(1000000000)


def check_file(filename):
    '''
    Checks if a file exists.

    Parameters :
    - filename : file to be checked
    Returns false if file doesn't exist, true if it exists.
    '''
    # load timestamps file
    if not os.path.isfile(filename):
        get_logger().critical('File doesn\'t exist : %s', filename)
        return False

    return True


def check_dict(param_dict, name, key_list=None):
    '''
    Checks if a parameter is a dictionary
    Param param_dict: parameter that should be a dictonary
    Param name: name of the parameter
    Param key_list: list of keys that should be present in the dict
    Returns true if parameter is a dictionary, throws error when it isn't
    '''
    if param_dict is None or type(param_dict) is not dict:
        raise TypeError("param %s should be a dictionary" % name)

    # check if key_list is defined
    if key_list is None:
        # key_list is not defined, no need to check keys
        return True
    else:
        # check if dictionary contains all keys in key_list
        return keys_in_dict(param_dict, key_list)


def keys_in_dict(param_dict, key_list):
    '''
    Checks if a list of keys exist in a dictionary
    Param param_dict: dictonary that should contain the keys
    Param key_list: key or list of keys that should be present in the dict
    Returns true if all keys were found in the dictionary
    '''
    if type(key_list) is str or type(key_list) is int:
        return key_list in param_dict
    elif not check_list(key_list, "key_list"):
        return False

    for key in key_list:
        if key not in param_dict:
            return False

    return True


def check_list(param_list, name):
    '''
    Checks if a parameter is a list
    Param param_list: parameter that should be a list
    Param name: name of the parameter
    Returns true if parameter is a list, throws error when it isn't
    '''
    if param_list is None or type(param_list) is not list:
        raise TypeError("param %s should be a list" % name)

    return True


def get_logger():
    '''
    Returns logger object
    '''
    return logging.getLogger(buildtimetrend.NAME)


def set_loglevel(loglevel):
    '''
    Sets loglevel
    Based on example on https://docs.python.org/2/howto/logging.html

    Assuming loglevel is bound to the string value obtained from the
    command line argument. Convert to upper case to allow the user to
    specify --log=DEBUG or --log=debug
    '''
    if loglevel is None or type(loglevel) is not str:
        raise TypeError("param %s should be a string" % 'loglevel')

    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)

    # create handler
    log_handler = logging.StreamHandler()
    log_handler.setLevel(numeric_level)

    # setup logger
    logger = get_logger()
    logger.setLevel(numeric_level)
    logger.addHandler(log_handler)
    logger.info("Set loglevel to %s (%d)", loglevel.upper(), numeric_level)
