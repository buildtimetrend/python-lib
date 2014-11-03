# vim: set expandtab sw=4 ts=4:
'''
Interface to Travis CI API.

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
import urllib2
import json
import re
import logging
from buildtimetrend.tools import check_file
from buildtimetrend.tools import check_dict
from buildtimetrend.build import Build
from buildtimetrend.settings import Settings
from buildtimetrend.stages import Stage
import buildtimetrend

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
    '''
    Loads Travis CI environment variables and assigns them to
    the corresponding settings item.
    '''
    if "TRAVIS" in os.environ and os.environ["TRAVIS"] is "true":

        settings = Settings()

        settings.add_setting("ci_platform", "travis")

        if "TRAVIS_BUILD_NUMBER" in os.environ:
            settings.add_setting("build", os.environ["TRAVIS_BUILD_NUMBER"])
        if "TRAVIS_BUILD_JOB" in os.environ:
            settings.add_setting("job", os.environ["TRAVIS_BUILD_JOB"])
        if "TRAVIS_BRANCH" in os.environ:
            settings.add_setting("branch", os.environ["TRAVIS_BRANCH"])
        if "TRAVIS_REPO_SLUG" in os.environ:
            settings.set_project_name(os.environ["TRAVIS_BRANCH"])

        if "TRAVIS_TEST_RESULT" in os.environ:
            # map $TRAVIS_TEST_RESULT to a more readable value
            if os.environ["TRAVIS_TEST_RESULT"] is 0:
                test_result = "passed"
            elif os.environ["TRAVIS_TEST_RESULT"] is 1:
                test_result = "failed"
            else:
                test_result = "errored"

            settings.add_setting("result", test_result)


class TravisData(object):
    '''
    Gather data from Travis CI using the API
    '''

    def __init__(self, repo, build_id):
        '''
        Retrieve Travis CI build data using the API.
        Param repo : github repository slug (fe. ruleant/buildtime-trend)
        Param build_id : Travis CI build id (fe. 158)
        '''
        self.build_data = {}
        self.build_jobs = {}
        self.current_job = Build()
        self.travis_substage = None
        self.repo = repo
        self.api_url = TRAVIS_ORG_API_URL
        self.build_id = str(build_id)

    def get_build_data(self):
        '''
        Retrieve Travis CI build data.
        '''
        request = 'repos/%s/builds?number=%s' % (self.repo, self.build_id)
        self.build_data = self.json_request(request)

        # log build_data
        logging.debug(
            "Build #%s data : %s",
            str(self.build_id),
            json.dumps(self.build_data, sort_keys=True, indent=2)
        )

    def process_build_jobs(self):
        '''
        Retrieve Travis CI build job data.
        '''
        if len(self.build_data) > 0:
            for job_id in self.build_data['builds'][0]['job_ids']:
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
        '''
        Retrieve Travis CI job data.
        '''
        request = 'jobs/%s' % str(job_id)
        job_data = self.json_request(request)

        # log job_data
        logging.debug(
            "Job #%s data : %s",
            str(job_id),
            json.dumps(job_data, sort_keys=True, indent=2)
        )

        return job_data

    def process_job_data(self, job_data):
        '''
        Process Job/build data and set build/job properties:
        - Build/job ID
        - build result : passed, failed, errored
        - git repo
        - git branch
        - CI platform : Travis
        '''
        self.current_job.add_property(
            "build",
            self.build_data['builds'][0]['number']
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

    def get_job_log(self, job_id):
        '''
        Retrieve Travis CI job log.
        '''
        request = 'jobs/%s/log' % str(job_id)
        request_url = self.api_url + request
        logging.info("Request build job log : %s", request_url)
        return urllib2.urlopen(request_url)

    def parse_job_log(self, job_id):
        '''
        Parse Travis CI job log.
        '''
        self.parse_job_log_stream(self.get_job_log(job_id))

    def parse_job_log_file(self, filename):
        '''
        Open a Travis CI log file and parse it.

        Parameters :
        - filename : filename of Travis CI log
        Returns false if file doesn't exist, true if it was read successfully.
        '''
        # load timestamps file
        if not check_file(filename):
            return False

        # read timestamps, calculate stage duration
        with open(filename, 'rb') as file_stream:
            self.parse_job_log_stream(file_stream)

        return True

    def parse_job_log_stream(self, stream):
        '''
        Parse Travis CI job log stream.
        '''
        self.travis_substage = TravisSubstage()

        for line in stream:
            # parse Travis CI timing tags
            if 'travis_' in line:
                self.parse_travis_time_tag(line)
            # parse Travis CI worker tag
            if 'Using worker:' in line:
                self.parse_travis_worker_tag(line)

    def parse_travis_time_tag(self, line):
        '''
        Parse and process Travis CI timing tags
        Param line : line from logfile containing Travis CI tags
        '''
        if self.travis_substage is None:
            self.travis_substage = TravisSubstage()

        escaped_line = line.replace('\x0d', '*').replace('\x1b', 'ESC')
        logging.debug('line : %s', escaped_line)

        # parse Travis CI timing tags
        for parse_string in TRAVIS_LOG_PARSE_TIMING_STRINGS:
            result = re.search(parse_string, line)
            if result:
                self.travis_substage.process_parsed_tags(result.groupdict())

                # when finished : log stage and create a new instance
                if self.travis_substage.has_finished():
                    # only log complete substages
                    if not self.travis_substage.finished_incomplete:
                        self.current_job.add_stage(self.travis_substage.stage)
                    self.travis_substage = TravisSubstage()

    def parse_travis_worker_tag(self, line):
        '''
        Parse and process Travis CI worker tag
        Param line : line from logfile containing Travis CI tags
        '''
        logging.debug('line : %s', line)

        # parse Travis CI worker tags
        result = re.search(TRAVIS_LOG_PARSE_WORKER_STRING, line)
        if not result:
            return

        worker_tags = result.groupdict()

        # check if parameter worker_tags is a dictionary and
        # if it contains all required tags
        tag_list = list({'hostname', 'os'})
        if check_dict(worker_tags, "worker_tags", tag_list):
            logging.debug("Worker tags : %s", worker_tags)
            self.current_job.add_property("worker", worker_tags)

    def json_request(self, json_request):
        '''
        Retrieve Travis CI data using API.
        '''
        req = urllib2.Request(
            self.api_url + json_request,
            None,
            {
                'user-agent': buildtimetrend.USER_AGENT,
                'accept': 'application/vnd.travis-ci.2+json'
            }
        )
        opener = urllib2.build_opener()
        result = opener.open(req)

        return json.load(result)

    def get_started_at(self):
        '''
        Retrieve timestamp when build was started.
        '''
        if len(self.build_data) > 0:
            return self.build_data['builds'][0]['started_at']
        else:
            return None

    def get_finished_at(self):
        '''
        Retrieve timestamp when build finished.
        '''
        if len(self.build_data) > 0:
            return self.build_data['builds'][0]['finished_at']
        else:
            return None


class TravisSubstage(object):
    '''
    Travis CI substage object, is constructed by feeding parsed tags
    from Travis CI logfile
    '''

    def __init__(self):
        '''
        Initialise Travis CI Substage object
        '''
        self.stage = Stage()
        self.timing_hash = ""
        self.finished_incomplete = False
        self.finished = False

    def process_parsed_tags(self, tags_dict):
        '''
        Processes parsed tags and calls the corresponding handler method
        Parameters:
        - tags_dict : dictionary with parsed tags
        '''
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
        '''
        Processes parsed start_stage tags
        Parameters:
        - tags_dict : dictionary with parsed tags
        '''
        # check if parameter tags_dict is a dictionary and
        # if it contains all required tags
        tag_list = list({'start_stage', 'start_substage'})
        if not check_dict(tags_dict, "tags_dict", tag_list):
            return False

        logging.debug("Start stage : %s", tags_dict)

        result = False

        if self.has_started():
            logging.warning("Substage already started")
        else:
            name = "%s.%s" % (
                tags_dict['start_stage'], tags_dict['start_substage']
            )
            result = self.stage.set_name(name)

        return result

    def process_start_time(self, tags_dict):
        '''
        Processes parsed start_time tags
        Parameters:
        - tags_dict : dictionary with parsed tags
        '''
        # check if parameter tags_dict is a dictionary and
        # if it contains all required tags
        if not check_dict(tags_dict, "tags_dict", 'start_hash'):
            return False

        logging.debug("Start time : %s", tags_dict)

        if self.has_timing_hash():
            logging.warning("Substage timing already set")
            return False

        self.timing_hash = tags_dict['start_hash']
        logging.info("Set timing hash : %s", self.timing_hash)

        return True

    def process_command(self, tags_dict):
        '''
        Processes parsed command tag
        Parameters:
        - tags_dict : dictionary with parsed tags
        '''
        # check if parameter tags_dict is a dictionary and
        # if it contains all required tags
        if not check_dict(tags_dict, "tags_dict", 'command'):
            return False

        logging.debug("Command : %s", tags_dict)

        result = False

        if self.has_command():
            logging.warning("Command is already set")
        elif self.stage.set_command(tags_dict['command']):
            logging.info("Set command : %s", tags_dict['command'])
            result = True

        return result

    def process_end_time(self, tags_dict):
        '''
        Processes parsed end_time tags
        Parameters:
        - tags_dict : dictionary with parsed tags
        '''
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

        logging.debug("End time : %s", tags_dict)

        result = False

        # check if timing was started
        # and if hash matches
        if (not self.has_timing_hash() or
                self.timing_hash != tags_dict['end_hash']):
            logging.warning("Substage timing was not started or \
                            hash doesn't match")
            self.finished_incomplete = True
        else:
            set_started = set_finished = set_duration = False

            # Set started timestamp
            if self.stage.set_started_at_nano(tags_dict['start_timestamp']):
                logging.info("Stage started at %s",
                             self.stage.data["started_at"]["isotimestamp"])
                set_started = True

            # Set finished timestamp
            if self.stage.set_finished_at_nano(tags_dict['finish_timestamp']):
                logging.info("Stage finished at %s",
                             self.stage.data["finished_at"]["isotimestamp"])
                set_finished = True

            # Set duration
            if self.stage.set_duration_nano(tags_dict['duration']):
                logging.info("Stage duration : %ss",
                             self.stage.data['duration'])
                set_duration = True

            result = set_started and set_finished and set_duration

        return result

    def process_end_stage(self, tags_dict):
        '''
        Processes parsed end_stage tags
        Parameters:
        - tags_dict : dictionary with parsed tags
        '''
        # check if parameter tags_dict is a dictionary and
        # if it contains all required tags
        tag_list = list({'end_stage', 'end_substage'})
        if not check_dict(tags_dict, "tags_dict", tag_list):
            return False

        logging.debug("End stage : %s", tags_dict)

        # construct substage name
        end_stagename = "%s.%s" % (
            tags_dict['end_stage'], tags_dict['end_substage']
        )

        # check if stage was started
        # and if substage name matches
        if not self.has_name() or self.stage.data["name"] != end_stagename:
            logging.warning("Substage was not started or name doesn't match")
            self.finished_incomplete = True
            return False

        # stage finished successfully
        self.finished = True
        logging.info("Stage %s finished successfully", self.get_name())

        return True

    def get_name(self):
        '''
        Return substage name, if it is not set, return the command
        '''
        if self.has_name():
            return self.stage.data["name"]
        elif self.has_command():
            return self.stage.data["command"]
        else:
            return ""

    def has_name(self):
        '''
        Checks if substage has a name
        Returns true if substage has a name
        '''
        return "name" in self.stage.data and \
            self.stage.data["name"] is not None and \
            len(self.stage.data["name"]) > 0

    def has_timing_hash(self):
        '''
        Checks if substage has a timing hash
        Returns true if substage has a timing hash
        '''
        return self.timing_hash is not None and len(self.timing_hash) > 0

    def has_command(self):
        '''
        Checks if a command is set for substage
        Returns true if a command is set
        '''
        return "command" in self.stage.data and \
            self.stage.data["command"] is not None and \
            len(self.stage.data["command"]) > 0

    def has_started(self):
        '''
        Checks if substage has started
        Returns true if substage has started
        '''
        return self.has_name() or self.has_timing_hash() or self.has_command()

    def has_finished(self):
        '''
        Checks if substage has finished.
        A substage is finished, if either the finished_timestamp is set,
        or if finished is (because of an error in parsing the tags).

        Returns true if substage has finished
        '''
        return self.finished_incomplete or \
            self.has_name() and self.finished or \
            not self.has_name() and self.has_timing_hash() and \
            "finished_at" in self.stage.data or \
            not self.has_name() and not self.has_timing_hash() and \
            self.has_command()
