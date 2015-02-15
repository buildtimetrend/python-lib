# vim: set expandtab sw=4 ts=4:
"""
Interface to Travis CI API.

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
import json
import re
from hashlib import sha256
from buildtimetrend.tools import get_logger
from buildtimetrend.tools import check_file
from buildtimetrend.tools import check_dict
from buildtimetrend.tools import check_num_string
from buildtimetrend.tools import get_repo_slug
from buildtimetrend.build import Build
from buildtimetrend.settings import Settings
from buildtimetrend.stages import Stage
import buildtimetrend
try:
    # For Python 3.0 and later
    from urllib.request import urlopen, Request, build_opener
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen, Request, build_opener

TRAVIS_ORG_API_URL = 'https://api.travis-ci.org/'

# strings to parse timestamps in Travis CI log file
TRAVIS_LOG_PARSE_TIMING_STRINGS = [
    r'travis_time:end:(?P<end_hash>.*):start=(?P<start_timestamp>\d+),'
    r'finish=(?P<finish_timestamp>\d+),duration=(?P<duration>\d+)\x0d\x1b',
    r'travis_fold:end:(?P<end_stage>\w+)\.(?P<end_substage>\d+)\x0d\x1b',
    r'travis_fold:start:(?P<start_stage>\w+)\.(?P<start_substage>\d+)\x0d\x1b',
    r'travis_time:start:(?P<start_hash>.*)\x0d\x1b\[0K',
    r'\$\ (?P<command>.*)\r',
]
TRAVIS_LOG_PARSE_WORKER_STRING = r'Using worker:\ (?P<hostname>.*):(?P<os>.*)'


def load_travis_env_vars():
    """
    Load Travis CI environment variables.

    Load Travis CI environment variables and assign their values to
    the corresponding setting value.
    """
    if "TRAVIS" in os.environ and os.environ["TRAVIS"] == "true":
        settings = Settings()

        # set ci_platform setting to "travis"
        settings.add_setting("ci_platform", "travis")

        # assign TRAVIS environment variable values to setting value
        settings.env_var_to_settings("TRAVIS_BUILD_NUMBER", "build")
        settings.env_var_to_settings("TRAVIS_JOB_NUMBER", "job")
        settings.env_var_to_settings("TRAVIS_BRANCH", "branch")
        settings.env_var_to_settings("TRAVIS_REPO_SLUG", "project_name")

        # convert and set Travis build result
        if "TRAVIS_TEST_RESULT" in os.environ:
            # map $TRAVIS_TEST_RESULT to a more readable value
            settings.add_setting(
                "result",
                convert_build_result(os.environ["TRAVIS_TEST_RESULT"])
            )


def convert_build_result(result):
    """
    Convert Travis build result to a more readable value.

    Parameters:
    - result : numerical build result
    """
    result = check_num_string(result, "result")

    if result is 0:
        build_result = "passed"
    elif result is 1:
        build_result = "failed"
    else:
        build_result = "errored"

    return build_result


def process_notification_payload(payload):
    """
    Load payload from Travis notification.

    Parameters:
    - payload : Travis CI notification payload
    """
    logger = get_logger()
    settings = Settings()

    if payload is None:
        logger.warning("Travis notification payload is not set")
        return

    if not type(payload) in (str, unicode):
        logger.warning("Travis notification payload is incorrect :"
                       " (unicode) string expected, got %s", type(payload))
        return

    json_payload = json.loads(payload)
    logger.info("Travis Payload : %r.", json_payload)

    # get repo name from payload
    if ("repository" in json_payload
            and "owner_name" in json_payload["repository"]
            and "name" in json_payload["repository"]):

        repo = get_repo_slug(json_payload["repository"]["owner_name"],
                             json_payload["repository"]["name"])

        logger.info("Build repo : %s", repo)
        settings.set_project_name(repo)

    # get build number from payload
    if "number" in json_payload:
        logger.info("Build number : %s", str(json_payload["number"]))
        settings.add_setting('build', json_payload['number'])


def check_authorization(repo, auth_header):
    """
    Check if Travis CI notification has a correct Authorization header.

    This check is enabled if travis_account_token is defined in settings.

    More information on the Authorization header :
    http://docs.travis-ci.com/user/notifications/#Authorization-for-Webhooks

    Returns true if Authorization header is valid, but also if
    travis_account_token is not defined.

    Parameters:
    - repo : git repo name
    - auth_header : Travis CI notification Authorization header
    """
    logger = get_logger()

    # get Travis account token from Settings
    token = Settings().get_setting("travis_account_token")

    # return True if token is not set
    if token is None:
        logger.info("Setting travis_account_token is not defined,"
                    " Travis CI notification Authorization header"
                    " is not checked.")
        return True

    # check if parameters are strings
    if type(repo) is str and type(auth_header) is str and type(token) is str:
        # generate hash and compare with Authorization header
        auth_hash = sha256(repo + token).hexdigest()

        if auth_hash == auth_header:
            logger.info("Travis CI notification Authorization header"
                        " is correct.")
            return True
        else:
            logger.error("Travis CI notification Authorization header"
                         " is incorrect.")
            return False
    else:
        logger.debug("repo, auth_header and travis_auth_token"
                     " should be strings.")
        return False


class TravisData(object):

    """ Gather data from Travis CI using the API. """

    def __init__(self, repo, build_id):
        """
        Retrieve Travis CI build data using the API.

        Parameters:
        - repo : github repository slug (fe. buildtimetrend/python-lib)
        - build_id : Travis CI build id (fe. 158)
        """
        self.build_data = {}
        self.build_jobs = {}
        self.build_config = {}
        self.current_job = Build()
        self.travis_substage = None
        self.repo = repo
        self.api_url = TRAVIS_ORG_API_URL
        self.build_id = str(build_id)

    def get_build_data(self):
        """ Retrieve Travis CI build data. """
        request = 'repos/%s/builds?number=%s' % (self.repo, self.build_id)
        self.build_data = self.json_request(request)

        # log build_data
        get_logger().debug(
            "Build #%s data : %s",
            str(self.build_id),
            json.dumps(self.build_data, sort_keys=True, indent=2)
        )

    def get_substage_name(self, command):
        """
        Resolve Travis CI substage name that corresponds to a cli command.

        Parameters:
        - command : cli command
        """
        if len(self.build_config) > 0:
            for stage_name, commands in self.build_config.items():
                if type(commands) is list and command in commands:
                    substage_number = commands.index(command) + 1
                    substage_name = "%s.%s" % (stage_name, substage_number)
                    get_logger().debug(
                        "Substage %s corresponds to '%s'",
                        substage_name, command
                    )
                    return substage_name

    def process_build_jobs(self):
        """ Retrieve Travis CI build job data. """
        if len(self.build_data) > 0 and "builds" in self.build_data:
            for build in self.build_data['builds']:
                if "config" in build:
                    self.build_config = build["config"]
                else:
                    self.build_config = {}

                if "job_ids" in build:
                    for job_id in build['job_ids']:
                        self.process_build_job(job_id)

    def process_build_job(self, job_id):
        """
        Retrieve Travis CI build job data.

        Parameters:
        - job_id : ID of the job to process
        """
        if job_id is None:
            return

        # retrieve job data from Travis CI
        job_data = self.get_job_data(job_id)
        # process build/job data
        self.process_job_data(job_data)
        # parse Travis CI job log file
        self.parse_job_log(job_id)

        # store build job
        self.build_jobs[str(job_id)] = self.current_job
        # create new build job instance
        self.current_job = Build()

    def get_job_data(self, job_id):
        """
        Retrieve Travis CI job data.

        Parameters:
        - job_id : ID of the job to process
        """
        request = 'jobs/%s' % str(job_id)
        job_data = self.json_request(request)

        # log job_data
        get_logger().debug(
            "Job #%s data : %s",
            str(job_id),
            json.dumps(job_data, sort_keys=True, indent=2)
        )

        return job_data

    def process_job_data(self, job_data):
        """
        Process Job/build data.

        Set build/job properties :
        - Build/job ID
        - build result : passed, failed, errored
        - git repo
        - git branch
        - CI platform : Travis

        Parameters:
        - job_data : dictionary with Travis CI job data
        """
        self.current_job.add_property(
            "build",
            # buildnumber is part before "." of job number
            job_data['job']['number'].split(".")[0]
        )
        self.current_job.add_property("job", job_data['job']['number'])
        self.current_job.add_property("branch", job_data['commit']['branch'])
        self.current_job.add_property(
            "repo",
            job_data['job']['repository_slug']
        )
        self.current_job.add_property("ci_platform", 'travis')
        self.current_job.add_property("result", job_data['job']['state'])
        self.current_job.set_started_at(job_data['job']['started_at'])
        self.current_job.set_finished_at(job_data['job']['finished_at'])

        # calculate job duration from start and finished timestamps
        # if no timing tags are available
        if not self.has_timing_tags():
            self.current_job.add_property("duration", self.get_job_duration())

    def get_job_log(self, job_id):
        """
        Retrieve Travis CI job log.

        Parameters:
        - job_id : ID of the job to process
        """
        request = 'jobs/%s/log' % str(job_id)
        request_url = self.api_url + request
        get_logger().info("Request build job log : %s", request_url)
        return urlopen(request_url)

    def parse_job_log(self, job_id):
        """
        Parse Travis CI job log.

        Parameters:
        - job_id : ID of the job to process
        """
        self.parse_job_log_stream(self.get_job_log(job_id))

    def parse_job_log_file(self, filename):
        """
        Open a Travis CI log file and parse it.

        Parameters :
        - filename : filename of Travis CI log
        Returns false if file doesn't exist, true if it was read successfully.
        """
        # load timestamps file
        if not check_file(filename):
            return False

        # read timestamps, calculate stage duration
        with open(filename, 'r') as file_stream:
            self.parse_job_log_stream(file_stream)

        return True

    def parse_job_log_stream(self, stream):
        """
        Parse Travis CI job log stream.

        Parameters:
        - stream : stream of job log file
        """
        self.travis_substage = TravisSubstage()
        check_timing_tags = self.has_timing_tags()

        for line in stream:
            # parse Travis CI timing tags
            if check_timing_tags and 'travis_' in line:
                self.parse_travis_time_tag(line)
            # parse Travis CI worker tag
            if 'Using worker:' in line:
                self.parse_travis_worker_tag(line)

    def parse_travis_time_tag(self, line):
        """
        Parse and process Travis CI timing tags.

        Parameters:
        - line : line from logfile containing Travis CI tags
        """
        if self.travis_substage is None:
            self.travis_substage = TravisSubstage()

        escaped_line = line.replace('\x0d', '*').replace('\x1b', 'ESC')
        get_logger().debug('line : %s', escaped_line)

        # parse Travis CI timing tags
        for parse_string in TRAVIS_LOG_PARSE_TIMING_STRINGS:
            result = re.search(parse_string, line)
            if result:
                self.travis_substage.process_parsed_tags(result.groupdict())

                # when finished : log stage and create a new instance
                if self.travis_substage.has_finished():
                    # set substage name, if it is not set
                    if not self.travis_substage.has_name() and \
                            self.travis_substage.has_command():
                        self.travis_substage.set_name(
                            self.get_substage_name(
                                self.travis_substage.get_command()
                            )
                        )

                    # only log complete substages
                    if not self.travis_substage.finished_incomplete:
                        self.current_job.add_stage(self.travis_substage.stage)
                    self.travis_substage = TravisSubstage()

    def parse_travis_worker_tag(self, line):
        """
        Parse and process Travis CI worker tag.

        Parameters:
        - line : line from logfile containing Travis CI tags
        """
        get_logger().debug('line : %s', line)

        # parse Travis CI worker tags
        result = re.search(TRAVIS_LOG_PARSE_WORKER_STRING, line)
        if not result:
            return

        worker_tags = result.groupdict()

        # check if parameter worker_tags is a dictionary and
        # if it contains all required tags
        tag_list = list({'hostname', 'os'})
        if check_dict(worker_tags, "worker_tags", tag_list):
            get_logger().debug("Worker tags : %s", worker_tags)
            self.current_job.add_property("worker", worker_tags)

    def json_request(self, json_request):
        """
        Retrieve Travis CI data using API.

        Parameters:
        - json_request : json_request to be sent to API
        """
        req = Request(
            self.api_url + json_request,
            None,
            {
                'user-agent': buildtimetrend.USER_AGENT,
                'accept': 'application/vnd.travis-ci.2+json'
            }
        )
        opener = build_opener()
        result = opener.open(req)

        return json.load(result)

    def has_timing_tags(self):
        """
        Check if Travis CI job log has timing tags.

        Timing tags were introduced on Travis CI starting 2014-08-07,
        check if started_at is more recent.
        """
        started_at = self.current_job.get_property("started_at")
        if started_at is None or "timestamp_seconds" not in started_at:
            return False

        # 1407369600 is epoch timestamp of 2014-08-07T00:00:00Z
        return started_at["timestamp_seconds"] > 1407369600

    def get_job_duration(self):
        """ Calculate build job duration. """
        started_at = self.current_job.get_property("started_at")
        finished_at = self.current_job.get_property("finished_at")
        if started_at is None or "timestamp_seconds" not in started_at or \
                finished_at is None or "timestamp_seconds" not in finished_at:
            return 0.0

        timestamp_start = float(started_at["timestamp_seconds"])
        timestamp_end = float(finished_at["timestamp_seconds"])
        return timestamp_end - timestamp_start

    def get_started_at(self):
        """ Retrieve timestamp when build was started. """
        if len(self.build_data) > 0:
            return self.build_data['builds'][0]['started_at']
        else:
            return None

    def get_finished_at(self):
        """ Retrieve timestamp when build finished. """
        if len(self.build_data) > 0:
            return self.build_data['builds'][0]['finished_at']
        else:
            return None


class TravisSubstage(object):

    """
    Travis CI substage object.

    It is constructed by feeding parsed tags from Travis CI logfile.
    """

    def __init__(self):
        """ Initialise Travis CI Substage object. """
        self.stage = Stage()
        self.timing_hash = ""
        self.finished_incomplete = False
        self.finished = False

    def process_parsed_tags(self, tags_dict):
        """
        Process parsed tags and calls the corresponding handler method.

        Parameters:
        - tags_dict : dictionary with parsed tags
        """
        result = False

        # check if parameter tags_dict is a dictionary
        if check_dict(tags_dict, "tags_dict"):
            if 'start_stage' in tags_dict:
                result = self.process_start_stage(tags_dict)
            elif 'start_hash' in tags_dict:
                result = self.process_start_time(tags_dict)
            elif 'command' in tags_dict:
                result = self.process_command(tags_dict)
            elif 'end_hash' in tags_dict:
                result = self.process_end_time(tags_dict)
            elif 'end_stage' in tags_dict:
                result = self.process_end_stage(tags_dict)

        return result

    def process_start_stage(self, tags_dict):
        """
        Process parsed start_stage tags.

        Parameters:
        - tags_dict : dictionary with parsed tags
        """
        # check if parameter tags_dict is a dictionary and
        # if it contains all required tags
        tag_list = list({'start_stage', 'start_substage'})
        if not check_dict(tags_dict, "tags_dict", tag_list):
            return False

        logger = get_logger()
        logger.debug("Start stage : %s", tags_dict)

        result = False

        if self.has_started():
            logger.warning("Substage already started")
        else:
            name = "%s.%s" % (
                tags_dict['start_stage'], tags_dict['start_substage']
            )
            result = self.set_name(name)

        return result

    def process_start_time(self, tags_dict):
        """
        Process parsed start_time tags.

        Parameters:
        - tags_dict : dictionary with parsed tags
        """
        # check if parameter tags_dict is a dictionary and
        # if it contains all required tags
        if not check_dict(tags_dict, "tags_dict", 'start_hash'):
            return False

        logger = get_logger()
        logger.debug("Start time : %s", tags_dict)

        if self.has_timing_hash():
            logger.warning("Substage timing already set")
            return False

        self.timing_hash = tags_dict['start_hash']
        logger.info("Set timing hash : %s", self.timing_hash)

        return True

    def process_command(self, tags_dict):
        """
        Process parsed command tag.

        Parameters:
        - tags_dict : dictionary with parsed tags
        """
        # check if parameter tags_dict is a dictionary and
        # if it contains all required tags
        if not check_dict(tags_dict, "tags_dict", 'command'):
            return False

        logger = get_logger()
        logger.debug("Command : %s", tags_dict)

        result = False

        if self.has_command():
            logger.warning("Command is already set")
        elif self.stage.set_command(tags_dict['command']):
            logger.info("Set command : %s", tags_dict['command'])
            result = True

        return result

    def process_end_time(self, tags_dict):
        """
        Process parsed end_time tags.

        Parameters:
        - tags_dict : dictionary with parsed tags
        """
        # check if parameter tags_dict is a dictionary and
        # if it contains all required tags
        tag_list = list({
            'end_hash',
            'start_timestamp',
            'finish_timestamp',
            'duration'
        })
        if not check_dict(tags_dict, "tags_dict", tag_list):
            return False

        logger = get_logger()
        logger.debug("End time : %s", tags_dict)

        result = False

        # check if timing was started
        # and if hash matches
        if (not self.has_timing_hash() or
                self.timing_hash != tags_dict['end_hash']):
            logger.warning("Substage timing was not started or"
                           " hash doesn't match")
            self.finished_incomplete = True
        else:
            set_started = set_finished = set_duration = False

            # Set started timestamp
            if self.stage.set_started_at_nano(tags_dict['start_timestamp']):
                logger.info("Stage started at %s",
                            self.stage.data["started_at"]["isotimestamp"])
                set_started = True

            # Set finished timestamp
            if self.stage.set_finished_at_nano(tags_dict['finish_timestamp']):
                logger.info("Stage finished at %s",
                            self.stage.data["finished_at"]["isotimestamp"])
                set_finished = True

            # Set duration
            if self.stage.set_duration_nano(tags_dict['duration']):
                logger.info("Stage duration : %ss",
                            self.stage.data['duration'])
                set_duration = True

            result = set_started and set_finished and set_duration

        return result

    def process_end_stage(self, tags_dict):
        """
        Process parsed end_stage tags.

        Parameters:
        - tags_dict : dictionary with parsed tags
        """
        # check if parameter tags_dict is a dictionary and
        # if it contains all required tags
        tag_list = list({'end_stage', 'end_substage'})
        if not check_dict(tags_dict, "tags_dict", tag_list):
            return False

        logger = get_logger()
        logger.debug("End stage : %s", tags_dict)

        # construct substage name
        end_stagename = "%s.%s" % (
            tags_dict['end_stage'], tags_dict['end_substage']
        )

        # check if stage was started
        # and if substage name matches
        if not self.has_name() or self.stage.data["name"] != end_stagename:
            logger.warning("Substage was not started or name doesn't match")
            self.finished_incomplete = True
            return False

        # stage finished successfully
        self.finished = True
        logger.info("Stage %s finished successfully", self.get_name())

        return True

    def get_name(self):
        """
        Return substage name.

        If name is not set, return the command.
        """
        if self.has_name():
            return self.stage.data["name"]
        elif self.has_command():
            return self.stage.data["command"]
        else:
            return ""

    def set_name(self, name):
        """
        Set substage name.

        Parameters:
        - name : substage name
        """
        return self.stage.set_name(name)

    def has_name(self):
        """
        Check if substage has a name.

        Returns true if substage has a name
        """
        return "name" in self.stage.data and \
            self.stage.data["name"] is not None and \
            len(self.stage.data["name"]) > 0

    def has_timing_hash(self):
        """
        Check if substage has a timing hash.

        Returns true if substage has a timing hash
        """
        return self.timing_hash is not None and len(self.timing_hash) > 0

    def has_command(self):
        """
        Check if a command is set for substage.

        Returns true if a command is set
        """
        return "command" in self.stage.data and \
            self.stage.data["command"] is not None and \
            len(self.stage.data["command"]) > 0

    def get_command(self):
        """ Return substage command. """
        if self.has_command():
            return self.stage.data["command"]
        else:
            return ""

    def has_started(self):
        """
        Check if substage has started.

        Returns true if substage has started
        """
        return self.has_name() or self.has_timing_hash() or self.has_command()

    def has_finished(self):
        """
        Check if substage has finished.

        A substage is finished, if either the finished_timestamp is set,
        or if finished is (because of an error in parsing the tags).

        Returns true if substage has finished
        """
        return self.finished_incomplete or \
            self.has_name() and self.finished or \
            not self.has_name() and self.has_timing_hash() and \
            "finished_at" in self.stage.data or \
            not self.has_name() and not self.has_timing_hash() and \
            self.has_command()
