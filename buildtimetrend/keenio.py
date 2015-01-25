# vim: set expandtab sw=4 ts=4:
'''
Interface to Keen IO.

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
'''

import os
from buildtimetrend.tools import get_logger
import copy
import keen
import requests
from keen import scoped_keys
from buildtimetrend.settings import Settings
from buildtimetrend.tools import check_file
from buildtimetrend.tools import check_dict
from buildtimetrend.tools import check_list


TIME_INTERVALS = {
    'week': {'name': 'week', 'timeframe': 'this_7_days'},
    'month': {'name': 'month', 'timeframe': 'this_30_days'},
    'year': {'name': 'year', 'timeframe': 'this_52_weeks'}
}


def keen_has_project_id():
    '''
    Check if Keen.io project ID is set.
    '''
    if "KEEN_PROJECT_ID" in os.environ or keen.project_id is not None:
        return True

    get_logger().warning("Keen.io Project ID is not set")
    return False


def keen_has_master_key():
    '''
    Check if Keen.io Master API key is set.
    '''
    # TODO remove try if master_key is part of the keen module
    try:
        if "KEEN_MASTER_KEY" in os.environ or keen.master_key is not None:
            return True
    except AttributeError:
        get_logger().debug("keen.master_key is not set")

    get_logger().warning("Keen.io Master API Key is not set")
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

    if keen_has_master_key() is None:
        logger.warning("Keen.io Read Key was not created,"
                       " keen.master_key is not defined.")
        return None

    # TODO remove try if master_key is part of the keen module
    try:
        master_key = keen.master_key
    except AttributeError:
        master_key = None

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


def get_dashboard_keen_config(repo):
    '''
    Generates a config file for the dashboard HTML file that contains the
    graphs generated by Keen.io
    '''
    logger = get_logger()

    # initialise config settings
    keen_config = {}

    if not keen_has_project_id() or not keen_has_master_key():
        logger.warning("Keen.io related config settings could not be created,"
                       " keen.project_id and/or keen.master_key"
                       " are not defined."
        )
        return keen_config

    # set keen project ID
    if keen.project_id is None:
        keen_project_id = os.environ["KEEN_PROJECT_ID"]
    else:
        keen_project_id = keen.project_id
    keen_config['projectId'] = str(keen_project_id)

    # generate read key
    read_key = keen_io_generate_read_key(repo)
    if read_key is not None:
        keen_config['readKey'] = str(read_key)

    # return keen config settings
    return keen_config


def get_dashboard_config(repo, extra=None):
    '''
    Generates a config file for the dashboard HTML file that contains the
    graphs generated by Keen.io
    Parameters:
    - repo : repo name (fe. buildtimetrend/service)
    - extra : dictionary of extra config settings, format : {"name" : "value"}
    '''
    # initialise config settings dictionaries
    config = {}
    keen_config = get_dashboard_keen_config(repo)

    # add repo and project name
    if repo is not None and not repo == "":
        # merge extra settings into existing config dictionary
        config.update({
            'projectName': str(repo),
            'repoName': str(repo)
        })

    # add extra config parameters
    if extra is not None and check_dict(extra, "extra"):
        config.update(extra)

    # create configuration as a string
    return "var config = %s;\nvar keenConfig = %s;" % (config, keen_config)


def generate_dashboard_config_file(repo):
    '''
    Generates a config file for the dashboard HTML file that contains the
    graphs generated by Keen.io
    '''
    logger = get_logger()

    # get config settings
    config_string = get_dashboard_config(repo)

    # write config file
    config_file = Settings().get_setting("dashboard_configfile")
    with open(config_file, 'w') as outfile:
        outfile.write(config_string)

    if check_file(config_file):
        logger.info("Created trends dashboard config file %s", config_file)
        return True
    else:
        logger.warning("The dashboard config file was not created")
        return False


def get_avg_buildtime(repo=None, interval=None):
    '''
    Query Keen.io database and retrieve average buildtime

    Parameters :
    - repo : repo name (fe. buildtimetrend/service)
    - interval : timeframe, possible values : 'week', 'month', 'year',
                 anything else defaults to 'week'
    '''
    if repo is None or not keen_is_readable():
        return -1

    timeframe = check_time_interval(interval)['timeframe']

    try:
        return keen.average(
            "builds",
            target_property="build.duration",
            timeframe=timeframe,
            filters=[get_repo_filter(repo)]
        )
    except requests.ConnectionError:
        get_logger().error("Connection to Keen.io API failed")
        return -1


def get_total_build_jobs(repo=None, interval=None):
    '''
    Query Keen.io database and retrieve total number of build jobs

    Parameters :
    - repo : repo name (fe. buildtimetrend/service)
    - interval : timeframe, possible values : 'week', 'month', 'year',
                 anything else defaults to 'week'
    '''
    if repo is None or not keen_is_readable():
        return -1

    timeframe = check_time_interval(interval)['timeframe']

    try:
        return keen.count_unique(
            "builds",
            target_property="build.job",
            timeframe=timeframe,
            filters=[get_repo_filter(repo)]
        )
    except requests.ConnectionError:
        get_logger().error("Connection to Keen.io API failed")
        return -1


def get_passed_build_jobs(repo=None, interval=None):
    '''
    Query Keen.io database and retrieve total number of build jobs that passed

    Parameters :
    - repo : repo name (fe. buildtimetrend/service)
    - interval : timeframe, possible values : 'week', 'month', 'year',
                 anything else defaults to 'week'
    '''
    if repo is None or not keen_is_readable():
        return -1

    timeframe = check_time_interval(interval)['timeframe']

    try:
        return keen.count_unique(
            "builds",
            target_property="build.job",
            timeframe=timeframe,
            filters=[
                get_repo_filter(repo),
                {
                    "property_name": "build.result",
                    "operator": "eq",
                    "property_value": "passed"
                }
            ]
        )
    except requests.ConnectionError:
        get_logger().error("Connection to Keen.io API failed")
        return -1


def get_pct_passed_build_jobs(repo=None, interval=None):
    '''
    Calculate percentage of passed build jobs.

    Parameters :
    - repo : repo name (fe. buildtimetrend/service)
    - interval : timeframe, possible values : 'week', 'month', 'year',
                 anything else defaults to 'week'
    '''
    total_jobs = get_total_build_jobs(repo, interval)
    passed_jobs = get_passed_build_jobs(repo, interval)

    get_logger().debug("passed/total build jobs : %d/%d",
                       passed_jobs, total_jobs)

    # calculate percentage if at least one job was executed
    # passed is a valid number (not -1)
    if total_jobs > 0 and passed_jobs >= 0:
        return int(float(passed_jobs) / float(total_jobs) * 100.0)

    return -1


def get_result_color(value=0, ok_thershold=90, warning_thershold=70):
    '''
    Get color code corresponding to result

    Parameters:
    - value : value to check
    - ok_thershold : OK threshold value
    - warning_thershold : warning thershold value
    '''
    if not(type(value) in (int, float) and
            type(ok_thershold) in (int, float) and
            type(warning_thershold) in (int, float)):
        return "lightgrey"

    # check thresholds
    if value >= ok_thershold:
        return "green"
    elif value >= warning_thershold:
        return "yellow"
    else:
        return "red"


def get_total_builds(repo=None, interval=None):
    '''
    Query Keen.io database and retrieve total number of builds

    Parameters :
    - repo : repo name (fe. buildtimetrend/service)
    - interval : timeframe, possible values : 'week', 'month', 'year',
                 anything else defaults to 'week'
    '''
    if repo is None or not keen_is_readable():
        return -1

    timeframe = check_time_interval(interval)['timeframe']

    try:
        return keen.count_unique(
            "builds",
            target_property="build.build",
            timeframe=timeframe,
            filters=[get_repo_filter(repo)]
        )
    except requests.ConnectionError:
        get_logger().error("Connection to Keen.io API failed")
        return -1


def get_latest_buildtime(repo=None):
    '''
    Query Keen.io database and retrieve buildtime duration of last build

    Parameters :
    - repo : repo name (fe. buildtimetrend/python-lib)
    '''
    if repo is None or not keen_is_readable():
        return -1

    try:
        result = keen.extraction(
            "builds",
            property_names="build.duration",
            latest=1,
            filters=[get_repo_filter(repo)]
        )
    except requests.ConnectionError:
        get_logger().error("Connection to Keen.io API failed")
        return -1

    if result is not None and len(result) > 0:
        return result[0]['build']['duration']

    return -1


def get_all_projects():
    '''
    Query Keen.io database and retrieve a list of all projects
    '''
    if not keen_is_readable():
        return []

    try:
        result = keen.select_unique("builds", "build.repo")
    except requests.ConnectionError:
        get_logger().error("Connection to Keen.io API failed")
        return []

    if type(result) is list:
        return result

    return []


def get_repo_filter(repo=None):
    '''
    Return filter for analysis request
    Parameters
    - repo : repo slug name, fe. buildtimetrend/python-lib
    '''
    if repo is None:
        return None

    return {
        "property_name": "build.repo",
        "operator": "eq",
        "property_value": str(repo)
    }


def check_time_interval(interval=None):
    '''
    Check time interval and returns corresponding parameters

    Parameters :
    - interval : timeframe, possible values : 'week', 'month', 'year',
                 anything else defaults to 'week'
    '''
    if type(interval) is str:
        # convert to lowercase
        interval = interval.lower()

        if interval in TIME_INTERVALS:
            return TIME_INTERVALS[interval]

    return TIME_INTERVALS['week']
