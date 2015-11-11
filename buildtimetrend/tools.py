# vim: set expandtab sw=4 ts=4:
"""
Collection of supporting functions.

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

from __future__ import division
import os
from buildtimetrend import logger
from datetime import datetime
from dateutil.parser import parse
from dateutil.tz import tzutc


def format_timestamp(timestamp):
    """
    Format a datetime timestamp (UTC) to ISO format (YYYY-MM-DDTHH:MM:SS).

    Parameters :
    - timestamp : timestamp, seconds since epoch
    """
    timestamp_datetime = datetime.utcfromtimestamp(timestamp)
    return timestamp_datetime.isoformat()


def split_timestamp(timestamp):
    """
    Split a timestamp in seperate components.

    Split a timestamp (expressed in seconds since epoch)
    in all seperate components :
      year, month, day of month, day of week,
      hour (12 and 24 hour), minute, second

    Parameters :
    - timestamp : timestamp, seconds since epoch
    """
    dt_utc = datetime.utcfromtimestamp(timestamp).replace(tzinfo=tzutc())
    return split_datetime(dt_utc)


def split_isotimestamp(isotimestamp):
    """
    Split a ISO formatted timestamp in seperate components.

    Split a timestamp (in ISO format)
    in all seperate components :
      year, month, day of month, day of week,
      hour (12 and 24 hour), minute, second

    Parameters :
    - isotimestamp : timestamp in ISO format YYYY-MM-DDTHH:MM:SS
    """
    if isotimestamp is None or type(isotimestamp) not in (str, unicode):
        raise TypeError(
            "param %s should be an isotimestamp formatted string, "
            "type %s found" %
            ('isotimestamp', type(isotimestamp))
        )
    # use dateutil.parser.parse to parse the timestamp
    return split_datetime(parse(isotimestamp, tzinfos={"UTC": +0}))


def split_datetime(timestamp_datetime):
    """
    Split a datetime timestamp in seperate components.

    Split a timestamp (is a datetime class instance)
    in all seperate components :
      year, month, day of month, day of week,
      hour (12 and 24 hour), minute, second

    Parameters :

    - timestamp_datetime : timestamp in datetime class format
    """
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
    """
    Convert time from nanoseconds to seconds.

    Parameters:
    - time : time in nanoseconds
    """
    return float(time) / float(1000000000)


def check_file(filename):
    """
    Check if a file exists.

    Parameters :
    - filename : file to be checked
    Return false if file doesn't exist, true if it exists.
    """
    # load timestamps file
    if not os.path.isfile(filename):
        logger.critical('File doesn\'t exist : %s', filename)
        return False

    return True


def file_is_newer(path1, path2):
    """
    Check if a file is newer than another file.

    Parameters :
    - path1 : path of first file
    - path2 : ipath of second file
    Return true if the first file is newer than the second one,
    return false if it is older, or if any of the files doesn't exist.
    """
    # check if files exist
    if not check_file(path1) or not check_file(path2):
        return False

    mtime1 = os.path.getmtime(path1)
    mtime2 = os.path.getmtime(path2)

    # check modification times
    return (mtime1 - mtime2) > 0


def is_dict(param_dict):
    """
    Return true if a parameter is a dictionary.

    Parameters :
    - param_dict: parameter that should be a dictonary
    Return true if parameter is a dictionary.
    """
    return param_dict is not None and type(param_dict) is dict


def check_dict(param_dict, name=None, key_list=None):
    """
    Check if a parameter is a dictionary.

    Returns True if it is a dictionary, false if it isn't,
    or if parameter 'name' is specified,
    an Error is raised with the name in the message.

    If key_list is defined,
    true is returned if the keys in key_list exits in the dictionary,
    false if they don't all exist.

    Parameters :
    - param_dict: parameter that should be a dictonary
    - name: name of the parameter
    - key_list: list of keys that should be present in the dict
    Return true if parameter is a dictionary, throws error when it isn't
    """
    if not is_dict(param_dict):
        if name is None:
            return False
        else:
            raise TypeError("param %s should be a dictionary" % name)

    # check if key_list is defined
    if key_list is None:
        # key_list is not defined, no need to check keys
        return True
    else:
        # check if dictionary contains all keys in key_list
        return keys_in_dict(param_dict, key_list)


def keys_in_dict(param_dict, key_list):
    """
    Check if a list of keys exist in a dictionary.

    Parameters :
    - param_dict: dictonary that should contain the keys
    - key_list: key or list of keys that should be present in the dict
    Return true if all keys were found in the dictionary
    """
    if type(key_list) in (str, int):
        return key_list in param_dict
    elif not is_list(key_list):
        return False

    for key in key_list:
        if key not in param_dict:
            return False

    return True


def is_list(param_list, name=None):
    """
    Check if a parameter is a list.

    Returns True if parameter is a list, false if it isn't,
    or if parameter 'name' is specified,
    an Error is raised with the name of the parameter in the message.

    Parameters :
    - param_list: parameter that should be a list
    - name: name of the parameter
    """
    if param_list is None or type(param_list) is not list:
        if name is None:
            return False
        else:
            raise TypeError("param %s should be a list" % name)

    return True


def is_string(param, name=None):
    """
    Check if a parameter is a string.

    Returns True if parameter is a string, false if it isn't,
    If parameter 'name' is specified,
    an Error is raised with the name of the parameter in the message.

    Parameters :
    - param: parameter that should be a string
    - name: name of the parameter
    """
    if param is None or type(param) is not str:
        if name is None:
            return False
        else:
            raise TypeError("param %s should be a string" % name)

    return True


def check_num_string(num_string, name):
    """
    Check if a parameter is an integer or numerical string.

    Parameters :
    - num_string: parameter that should be a numerical string
    - name: name of the parameter
    Return integer of numerical string, throws error when it isn't
    """
    if num_string is None or type(num_string) not in (str, int):
        raise TypeError(
            "param %s should be a numerical string or an integer" % name
        )

    return int(num_string)


def get_repo_slug(repo_owner=None, repo_name=None):
    """
    Return repo slug.

    This function concatenates repo_owner and repo_name,
    fe. buildtimetrend/service

    Parameters :
    - repo_owner : name of the Github repo owner, fe. `buildtimetrend`
    - repo_name : name of the Github repo, fe. `service`
    """
    if repo_owner is not None and repo_name is not None:
        return "%s/%s" % (str(repo_owner), str(repo_name))
    else:
        return None
