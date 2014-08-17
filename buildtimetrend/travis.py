'''
vim: set expandtab sw=4 ts=4:

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

TRAVIS_API_URL = 'https://api.travis-ci.org/'

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
        self.build_id = str(build_id)

    def get_build_data(self):
        '''
        Retrieve Travis CI build data.
        '''
        self.build_data = self.json_request('repos/' + self.repo
            + '/builds?number=' + self.build_id)

    def get_build_jobs(self):
        '''
        Retrieve Travis CI build job data.
        '''
        if len(self.build_data) > 0 and len(self.build_data['builds'][0]['job_ids']) > 0:
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
        request_url = TRAVIS_API_URL + 'jobs/' + str(job_id) + '/log'
        print "Request build job log : " + request_url
        return urllib2.urlopen(request_url)

    def json_request(self, json_request):
        '''
        Retrieve Travis CI data using API.
        '''
        req = urllib2.Request(
            TRAVIS_API_URL + json_request,
            None,
            {
                # get version from Config class
                'user-agent': 'buildtime-trend/0.2-dev',
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
