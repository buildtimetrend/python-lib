# vim: set expandtab sw=4 ts=4:
'''
Interface to Keen IO.

Copyright (C) 2014 Dieter Adriaenssens <ruleant@users.sourceforge.net>

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
'''

import os
from buildtimetrend.tools import get_logger
import copy
import keen
from keen import scoped_keys
from buildtimetrend.settings import Settings
from buildtimetrend.tools import check_file
from buildtimetrend.tools import check_dict
from buildtimetrend.tools import check_list
from buildtimetrend.tools import check_interval


def keen_has_project_id():
    '''
    Check if Keen.io project ID is set.
    '''
    if "KEEN_PROJECT_ID" in os.environ or keen.project_id is not None:
        return True

    get_logger().warning("Keen.io Project ID is not set")
    return False


def keen_is_writable():
    '''
    Check if login keys for Keen IO API are set, to allow writing.
    '''
    if (keen_has_project_id() and
            "KEEN_WRITE_KEY" in os.environ or keen.write_key is not None):
        return True

    get_logger().warning("Keen.io Write Key is not set")
    return False


def keen_is_readable():
    '''
    Check if login keys for Keen IO API are set, to allow reading.
    '''
    if (keen_has_project_id() and
            "KEEN_READ_KEY" in os.environ or keen.read_key is not None):
        return True

    get_logger().warning("Keen.io Read Key is not set")
    return False


def keen_io_generate_read_key(repo):
    '''
    Create scoped key for reading only the build-stages related data.
    Param repo : github repository slug (fe. buildtimetrend/python-lib)
    '''
    logger = get_logger()

    if "KEEN_MASTER_KEY" in os.environ:
        master_key = os.getenv("KEEN_MASTER_KEY")
        privileges = {
            "filters": [{
                "property_name": "build.repo",
                "operator": "eq",
                "property_value": repo
            }],
            "allowed_operations": ["read"]
        }

        logger.info("Keen.io Read Key is created for %s", repo)
        return scoped_keys.encrypt(master_key, privileges)

    logger.warning("Keen.io Read Key was not created.")
    return None


def log_build_keen(build):
    '''Send build data to keen.io'''
    if keen_is_writable():
        get_logger().info("Sending data to Keen.io")
        keen_add_event("builds", {"build": build.to_dict()})
        keen_add_events("build_stages", build.stages_to_list())


def keen_add_event(event_collection, payload):
    '''
    Wrapper for keen.add_event(), adds project info
    Param event_collection : collection event data is submitted to
    Param payload : data that is submitted
    '''
    # add project info to this event
    payload = add_project_info_dict(payload)

    # submit list of events to Keen.io
    keen.add_event(event_collection, payload)


def keen_add_events(event_collection, payload):
    '''
    Wrapper for keen.add_events(), adds project info to each event
    Param event_collection : collection event data is submitted to
    Param payload : array of events that is submitted
    '''
    # add project info to each event
    payload = add_project_info_list(payload)

    # submit list of events to Keen.io
    keen.add_events({event_collection: payload})


def add_project_info_dict(payload):
    '''
    Adds project info to a dictonary
    Param payload: dictonary payload
    '''
    if not check_dict(payload, "payload"):
        return None

    payload_as_dict = copy.deepcopy(payload)

    payload_as_dict["buildtime_trend"] = Settings().get_project_info()

    # override timestamp, set to finished_at timestamp
    if "build" in payload and "finished_at" in payload["build"]:
        payload_as_dict["keen"] = {
            "timestamp": payload["build"]["finished_at"]["isotimestamp"]
        }

    return payload_as_dict


def add_project_info_list(payload):
    '''
    Adds project info to a list of dictionaries
    Param payload: list of dictionaries
    '''
    if not check_list(payload, "payload"):
        return None

    payload_as_list = []

    # loop over dicts in payload and add project info to each one
    for event_dict in payload:
        payload_as_list.append(add_project_info_dict(event_dict))

    return payload_as_list


def generate_overview_config_file(repo):
    '''
    Generates a config file for the overview HTML file that contains the
    graphs generated by Keen.io
    '''
    logger = get_logger()

    if not ("BUILD_TREND_SAMPLE_CONFIGFILE" in os.environ
            and "BUILD_TREND_CONFIGFILE" in os.environ
            and "KEEN_PROJECT_ID" in os.environ):
        logger.error("Trends overview config file was not created")
        return

    sample_filename = os.getenv("BUILD_TREND_SAMPLE_CONFIGFILE")
    config_file = os.getenv("BUILD_TREND_CONFIGFILE")
    keen_project_id = os.getenv("KEEN_PROJECT_ID")

    # check if sample config file exists
    if not check_file(sample_filename):
        return

    # generate read key
    read_key = keen_io_generate_read_key(repo)

    # list of string pairs to be replaced (search string : new string)
    replacements = {
        'keen_project_id': str(keen_project_id),
        'keen_read_key': str(read_key),
        'project_name': str(repo)
    }

    with open(sample_filename, 'rb') as infile, \
            open(config_file, 'w') as outfile:
        for line in infile:
            for src, target in replacements.iteritems():
                line = line.replace(src, target)
            outfile.write(line)

    logger.info("Created trends overview config file")


def get_avg_buildtime(repo, interval=None):
    '''
    Query Keen.io database and retrieve average buildtime

    Parameters :
    - repo : repo name (fe. buildtimetrend/service)
    - interval : timeframe, possible values : 'week', 'month', 'year',
                 anything else defaults to 'week'
    '''
    if repo is None or not keen_is_readable():
        return None

    timeframe = check_interval(interval)['timeframe']

    return keen.average(
        "builds",
        target_property="build.duration",
        timeframe=timeframe,
        filters=[{
            "property_name": "build.repo",
            "operator": "eq",
            "property_value": str(repo)
        }]
    )


def get_latest_buildtime(repo):
    '''
    Query Keen.io database and retrieve buildtime duration of last build

    Parameters :
    - repo : repo name (fe. buildtimetrend/python-lib)
    '''
    if repo is None or not keen_is_readable():
        return None

    result = keen.extraction(
        "builds",
        property_names="build.duration",
        latest=1,
        filters=[{
            "property_name": "build.repo",
            "operator": "eq",
            "property_value": str(repo)
        }]
    )

    if result is not None and len(result) > 0:
        return result[0]['build']['duration']

    return None
