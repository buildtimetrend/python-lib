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
from builtins import str
import codecs
import json
from buildtimetrend import logger
from buildtimetrend.tools import check_dict
import buildtimetrend
try:
    # For Python 3.0 and later
    from urllib.request import Request, build_opener
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import Request, build_opener

TRAVIS_ORG_API_URL = 'https://api.travis-ci.org/'


class TravisConnector(object):

    """Base class to connect to Travis CI API."""

    def __init__(self):
        """Constructor."""
        self.api_url = None
        self.request_params = {
            'user-agent': buildtimetrend.USER_AGENT
        }

    def download_job_log(self, job_id):
        """
        Retrieve Travis CI job log.

        Parameters:
        - job_id : ID of the job to process
        """
        request = 'jobs/{}/log'.format(str(job_id))
        logger.info("Request build job log #%s", str(job_id))
        return self._handle_request(request)

    def json_request(self, json_request):
        """
        Retrieve Travis CI data using API.

        Parameters:
        - json_request : json_request to be sent to API
        """
        result = self._handle_request(
            json_request,
            {
                'accept': 'application/vnd.travis-ci.2+json'
            }
        )

        reader = codecs.getreader('utf-8')
        return json.load(reader(result))

    def _handle_request(self, request, params=None):
        """
        Retrieve Travis CI data using API.

        Parameters:
        - request : request to be sent to API
        - params : HTTP request parameters
        """
        request_url = self.api_url + request

        request_params = self.request_params.copy()
        if params is not None and check_dict(params, "params"):
            request_params.update(params)

        req = Request(
            request_url,
            None,
            request_params
        )
        opener = build_opener()
        logger.info("Request from Travis CI API : %s", request_url)
        return opener.open(req)


class TravisOrgConnector(TravisConnector):

    """Connects to Travis.org API."""

    def __init__(self):
        """Constructor."""
        super(TravisOrgConnector, self).__init__()
        self.api_url = TRAVIS_ORG_API_URL
