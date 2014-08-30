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
import buildtimetrend

TRAVIS_ORG_API_URL = 'https://api.travis-ci.org/'

# strings to parse timestamps in Travis CI log file
TRAVIS_LOG_PARSE_STRINGS = [
    r'travis_time:end:(?P<end_hash>.*):start=(?P<start_timestamp>\d+),finish=(?P<finish_timestamp>\d+),duration=(?P<duration>\d+)\x0d\x1b',
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
        for line in stream:
            if 'travis_' in line:
                print 'line : ' + line.replace('\x0d', '*').replace('\x1b', 'ESC')

                # parse Travis CI timing tags
                for parse_string in TRAVIS_LOG_PARSE_STRINGS:
                    result = re.search(parse_string, line)
                    if result:
                        print result.groupdict()

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
