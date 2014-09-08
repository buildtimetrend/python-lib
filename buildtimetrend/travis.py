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
import urllib2
import json
import re
from buildtimetrend.tools import check_file
from buildtimetrend.tools import check_dict
import buildtimetrend

TRAVIS_ORG_API_URL = 'https://api.travis-ci.org/'

# strings to parse timestamps in Travis CI log file
TRAVIS_LOG_PARSE_STRINGS = [
    r'travis_time:end:(?P<end_hash>.*):start=(?P<start_timestamp>\d+),'
    r'finish=(?P<finish_timestamp>\d+),duration=(?P<duration>\d+)\x0d\x1b',
    r'travis_fold:end:(?P<end_stage>\w+)\.(?P<end_substage>\d+)\x0d\x1b',
    r'travis_fold:start:(?P<start_stage>\w+)\.(?P<start_substage>\d+)\x0d\x1b',
    r'travis_time:start:(?P<start_hash>.*)\x0d\x1b\[0K',
    r'\$\ (?P<command>.*)\r',
]


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
        self.jobs_data = {}
        self.repo = repo
        self.api_url = TRAVIS_ORG_API_URL
        self.build_id = str(build_id)

    def get_build_data(self):
        '''
        Retrieve Travis CI build data.
        '''
        request = 'repos/' + self.repo + '/builds?number=' + self.build_id
        self.build_data = self.json_request(request)

    def get_build_jobs(self):
        '''
        Retrieve Travis CI build job data.
        '''
        if len(self.build_data) > 0:
            for job_id in self.build_data['builds'][0]['job_ids']:
                self.get_job_data(job_id)

    def get_job_data(self, job_id):
        '''
        Retrieve Travis CI job data.
        '''
        self.jobs_data[str(job_id)] = self.json_request('jobs/' + str(job_id))

    def get_job_log(self, job_id):
        '''
        Retrieve Travis CI job log.
        '''
        request_url = self.api_url + 'jobs/' + str(job_id) + '/log'
        print "Request build job log : " + request_url
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
        substage = TravisSubstage()

        for line in stream:
            if 'travis_' in line:
                print 'line : ' + line.replace('\x0d', '*').replace('\x1b', 'ESC')

                # parse Travis CI timing tags
                for parse_string in TRAVIS_LOG_PARSE_STRINGS:
                    result = re.search(parse_string, line)
                    if result:
                        substage.process_parsed_tags(result.groupdict())

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


class TravisSubstage(object):
    '''
    Travis CI substage object, is constructed by feeding parsed tags
    from Travis CI logfile
    '''

    def __init__(self):
        '''
        Initialise Travis CI Substage object
        '''
        self.name = ""
        self.timing_hash = ""
        self.command = ""
        self.start_timestamp = 0
        self.finish_timestamp = 0
        self.duration = 0
        self.finished_incomplete = False

    def process_parsed_tags(self, tags_dict):
        '''
        Processes parsed tags and calls the corresponding handler method
        Parameters:
        - tags_dict : dictionary with parsed tags
        '''
        # check if parameter tags_dict is a dictionary
        if not check_dict(tags_dict, "tags_dict"):
            return False

        if 'start_stage' in tags_dict:
            self.process_start_stage(tags_dict)
        elif 'start_hash' in tags_dict:
            self.process_start_time(tags_dict)
        elif 'command' in tags_dict:
            self.process_command(tags_dict)
        elif 'end_hash' in tags_dict:
            self.process_end_time(tags_dict)
        elif 'end_stage' in tags_dict:
            self.process_end_stage(tags_dict)

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

        print "Start stage : %s" % tags_dict

        if self.has_started():
            print "Substage already started"
            return False

        self.name = "%s.%s" % (
            tags_dict['start_stage'], tags_dict['start_substage']
        )
        print "Set name : %s" % self.name

        return True

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

        print "Start time : %s" % tags_dict

        if self.has_timing_hash():
            print "Substage timing already set"
            return False

        self.timing_hash = tags_dict['start_hash']
        print "Set timing hash : %s" % self.timing_hash

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

        print "Command : %s" % tags_dict

        if self.command is not None and len(self.command) > 0:
            print "Command is already set"
            return False

        self.command = tags_dict['command']
        print "Set command : %s" % self.command

        # use command as substage name if name is not set
        if not self.has_name():
            self.name = self.command

        return True

    def process_end_time(self, tags_dict):
        '''
        Processes parsed end_time tags
        Parameters:
        - tags_dict : dictionary with parsed tags
        '''
        tag_list = list({
            'end_hash',
            'start_timestamp',
            'finish_timestamp',
            'duration'
        })
        if not check_dict(tags_dict, "tags_dict", tag_list):
            return False

        print "End time : %s" % tags_dict

        # check if timing was started
        # and if hash matches
        if (not self.has_timing_hash() or
                self.timing_hash != tags_dict['end_hash']):
            print "Substage timing was not started or hash doesn't match"
            self.finished_incomplete = True
            return False

        self.start_timestamp = tags_dict['start_timestamp']
        self.finish_timestamp = tags_dict['finish_timestamp']
        self.duration = tags_dict['duration']

        return True

    def process_end_stage(self, tags_dict):
        '''
        Processes parsed end_stage tags
        Parameters:
        - tags_dict : dictionary with parsed tags
        '''
        if check_dict(tags_dict, "tags_dict"):
            print "End stage : %s" % tags_dict

    def has_name(self):
        '''
        Checks if substage has a name
        Returns true if substage has a name
        '''
        return self.name is not None and len(self.name) > 0

    def has_timing_hash(self):
        '''
        Checks if substage has a timing hash
        Returns true if substage has a timing hash
        '''
        return self.timing_hash is not None and len(self.timing_hash) > 0

    def has_started(self):
        '''
        Checks if substage has started
        Returns true if substage has started
        '''
        return self.has_name() or self.has_timing_hash()

    def has_finished(self):
        '''
        Checks if substage has finished.
        A substage is finished, if either the finished_timestamp is set,
        or if finished is (because of an error in parsing the tags).

        Returns true if substage has finished
        '''
        return self.finished_incomplete or self.finish_timestamp > 0
