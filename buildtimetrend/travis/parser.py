# vim: set expandtab sw=4 ts=4:
"""
Functions and classes to retrieve and parse Travis CI build data.

Copyright (C) 2014-2016 Dieter Adriaenssens <ruleant@users.sourceforge.net>

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
from builtins import str
from builtins import object
import re
import json
from buildtimetrend import logger
from buildtimetrend import tools
from buildtimetrend.buildjob import BuildJob
from buildtimetrend.collection import Collection
from buildtimetrend.travis.connector import TravisOrgConnector
from buildtimetrend.travis.connector import TravisConnector
from buildtimetrend.travis.substage import TravisSubstage
try:
    # For Python 3.0 and later
    from urllib.error import HTTPError, URLError
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import HTTPError, URLError


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


class TravisData(object):

    """Gather data from Travis CI using the API."""

    def __init__(self, repo, build_id, connector=None):
        """
        Retrieve Travis CI build data using the API.

        Parameters:
        - repo : github repository slug (fe. buildtimetrend/python-lib)
        - build_id : Travis CI build id (fe. 158)
        - connector : Travis Connector instance
        """
        self.builds_data = {}
        self.build_jobs = {}
        self.current_build_data = {}
        self.current_job = BuildJob()
        self.travis_substage = None
        self.repo = repo
        self.build_id = str(build_id)
        # set TravisConnector if it is defined
        if isinstance(connector, TravisConnector):
            self.connector = connector
        # use Travis Org connector by default
        else:
            self.connector = TravisOrgConnector()

    def get_build_data(self):
        """
        Retrieve Travis CI build data.

        Returns true if retrieving data was succesful, false on error.
        """
        request = 'repos/{repo}/builds?number={build_id}'.format(
            repo=self.repo, build_id=self.build_id
        )
        try:
            self.builds_data = self.connector.json_request(request)
        except (HTTPError, URLError) as msg:
            logger.error("Error getting build data from Travis CI: %s", msg)
            return False

        # log builds_data
        logger.debug(
            "Build #%s data : %s",
            str(self.build_id),
            json.dumps(self.builds_data, sort_keys=True, indent=2)
        )

        return True

    def get_substage_name(self, command):
        """
        Resolve Travis CI substage name that corresponds to a cli command.

        Parameters:
        - command : cli command
        """
        if not tools.is_string(command):
            return ""

        if len(self.current_build_data) > 0 and \
                "config" in self.current_build_data:
            build_config = self.current_build_data["config"]
        else:
            logger.warning(
                "Travis CI build config is not set"
            )
            return ""

        # check if build_config collection is empty
        if build_config:
            for stage_name, commands in build_config.items():
                if tools.is_list(commands) and command in commands:
                    substage_number = commands.index(command) + 1
                    substage_name = "{stage}.{substage:d}".format(
                        stage=stage_name, substage=substage_number
                    )
                    logger.debug(
                        "Substage %s corresponds to '%s'",
                        substage_name, command
                    )
                    return substage_name

        return ""

    def process_build_jobs(self):
        """
        Retrieve Travis CI build job data.

        Method is a generator, iterate result to get each processed build job.
        """
        if len(self.builds_data) > 0 and "builds" in self.builds_data:
            for build in self.builds_data['builds']:
                self.current_build_data = build

                if "job_ids" in build:
                    for job_id in build['job_ids']:
                        yield self.process_build_job(job_id)

            # reset current_build_data after builds are processed
            self.current_build_data = {}

    def process_build_job(self, job_id):
        """
        Retrieve Travis CI build job data.

        Parameters:
        - job_id : ID of the job to process
        """
        if job_id is None:
            return None

        # retrieve job data from Travis CI
        job_data = self.get_job_data(job_id)
        # process build/job data
        self.process_job_data(job_data)
        # parse Travis CI job log file
        self.parse_job_log(job_id)

        # store build job
        self.build_jobs[str(job_id)] = self.current_job
        # create new build job instance
        self.current_job = BuildJob()

        # return processed build job
        return self.build_jobs[str(job_id)]

    def get_job_data(self, job_id):
        """
        Retrieve Travis CI job data.

        Parameters:
        - job_id : ID of the job to process
        """
        request = 'jobs/{:s}'.format(str(job_id))
        job_data = self.connector.json_request(request)

        # log job_data
        logger.debug(
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
        - build matrix (language, language version, compiler, ...)
        - build_trigger : push, pull_request
        - pull_request (is_pull_request, title, number)

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

        self.set_build_matrix(job_data)

        self.process_pull_request_data()

        self.current_job.set_started_at(job_data['job']['started_at'])
        self.current_job.set_finished_at(job_data['job']['finished_at'])

        # calculate job duration from start and finished timestamps
        # if no timing tags are available
        if not self.has_timing_tags():
            self.current_job.add_property("duration", self.get_job_duration())

    def set_build_matrix(self, job_data):
        """
        Retrieve build matrix data from job data and store in properties.

        Properties :
        - language
        - language version (if applicable)
        - compiler (if applicable)
        - operating system
        - environment parameters

        Parameters:
        - job_data : dictionary with Travis CI job data
        """
        # check if job config data exists
        if 'job' not in job_data or 'config' not in job_data['job']:
            logger.warning("Job config data doesn't exist")
            return

        build_matrix = Collection()
        job_config = job_data['job']['config']

        if 'language' in job_config:
            language = job_config['language']
            build_matrix.add_item('language', language)

            # set language version
            # ('d', 'dart', 'go', 'perl', 'php', 'python', 'rust')
            if language in job_config:
                if language == 'android':
                    build_matrix.add_item(
                        "language_components",
                        " ".join(job_config[language]["components"])
                    )
                else:
                    build_matrix.add_item(
                        'language_version',
                        str(job_config[language])
                    )

        # language specific build matrix parameters
        parameters = {
            'ghc': 'ghc',  # Haskell
            'jdk': 'jdk',  # Java, Android, Groovy, Ruby, Scala
            'lein': 'lein',  # Clojure
            'mono': 'mono',  # C#, F#, Visual Basic
            'node_js': 'node_js',  # Javascript
            'otp_release': 'otp_release',  # Erlang
            'rvm': 'rvm',  # Ruby, Objective-C
            'gemfile': 'gemfile',  # Ruby, Objective-C
            'xcode_sdk': 'xcode_sdk',  # Objective-C
            'xcode_scheme': 'xcode_scheme',  # Objective-C
            'compiler': 'compiler',  # C, C++
            'os': 'os',
            'env': 'parameters'
        }
        for parameter, name in parameters.items():
            if parameter in job_config:
                build_matrix.add_item(name, str(job_config[parameter]))

        self.current_job.add_property(
            "build_matrix",
            build_matrix.get_items_with_summary()
        )

    def process_pull_request_data(self):
        """Retrieve pull request data from Travis CI API."""
        # check if collection is empty
        if self.current_build_data:
            if "event_type" in self.current_build_data:
                # build trigger (push or pull_request)
                self.current_job.add_property(
                    "build_trigger",
                    self.current_build_data["event_type"]
                )

            # pull_request
            pull_request_data = {}
            if "pull_request" in self.current_build_data:
                pull_request_data["is_pull_request"] = \
                    self.current_build_data["pull_request"]
            else:
                pull_request_data["is_pull_request"] = False

            if "pull_request_title" in self.current_build_data:
                pull_request_data["title"] = \
                    self.current_build_data["pull_request_title"]

            if "pull_request_number" in self.current_build_data:
                pull_request_data["number"] = \
                    self.current_build_data["pull_request_number"]

            self.current_job.add_property("pull_request", pull_request_data)

    def parse_job_log(self, job_id):
        """
        Parse Travis CI job log.

        Parameters:
        - job_id : ID of the job to process
        """
        self.parse_job_log_stream(self.connector.download_job_log(job_id))

    def parse_job_log_file(self, filename):
        """
        Open a Travis CI log file and parse it.

        Parameters :
        - filename : filename of Travis CI log
        Returns false if file doesn't exist, true if it was read successfully.
        """
        # load timestamps file
        if not tools.check_file(filename):
            return False

        # read timestamps, calculate stage duration
        with open(filename, 'rb') as file_stream:
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
            # convert to str if line is bytes type
            if isinstance(line, bytes):
                line = line.decode('utf-8')
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
        logger.debug('line : %s', escaped_line)

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
        logger.debug('line : %s', line)

        # parse Travis CI worker tags
        result = re.search(TRAVIS_LOG_PARSE_WORKER_STRING, line)
        if not result:
            return

        worker_tags = result.groupdict()

        # check if parameter worker_tags is a dictionary and
        # if it contains all required tags
        tag_list = list({'hostname', 'os'})
        if tools.check_dict(worker_tags, "worker_tags", tag_list):
            logger.debug("Worker tags : %s", worker_tags)
            self.current_job.add_property("worker", worker_tags)

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
        """Calculate build job duration."""
        started_at = self.current_job.get_property("started_at")
        finished_at = self.current_job.get_property("finished_at")
        if started_at is None or "timestamp_seconds" not in started_at or \
                finished_at is None or "timestamp_seconds" not in finished_at:
            return 0.0

        timestamp_start = float(started_at["timestamp_seconds"])
        timestamp_end = float(finished_at["timestamp_seconds"])
        return timestamp_end - timestamp_start

    def get_started_at(self):
        """Retrieve timestamp when build was started."""
        if tools.check_dict(self.current_build_data, key_list=["started_at"]):
            return self.current_build_data['started_at']
        else:
            return None

    def get_finished_at(self):
        """Retrieve timestamp when build finished."""
        if tools.check_dict(self.current_build_data, key_list=["finished_at"]):
            return self.current_build_data['finished_at']
        else:
            return None
