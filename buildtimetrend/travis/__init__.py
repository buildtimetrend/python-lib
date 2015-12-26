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
from builtins import object
import os
import json
from hashlib import sha256
from buildtimetrend import logger
from buildtimetrend.tools import check_num_string
from buildtimetrend.tools import is_string
from buildtimetrend.tools import get_repo_slug
from buildtimetrend.settings import Settings
from buildtimetrend.collection import Collection
from buildtimetrend.travis.parser import TravisData
import buildtimetrend


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
    Extract repo slug and build number from Travis notification payload.

    Returns a dictionary with "repo" and "build" information,
    or an empty dictionary if the payload could not be processed.

    Deprecated behaviour : Currently the repo and build information are
    also stored in the "settings" object,
    but this will be removed in the near future.

    Parameters:
    - payload : Travis CI notification payload
    """
    settings = Settings()
    parameters = {}

    if payload is None:
        logger.warning("Travis notification payload is not set")
        return parameters

    if not is_string(payload):
        logger.warning("Travis notification payload is incorrect :"
                       " string expected, got %s", type(payload))
        return parameters

    json_payload = json.loads(payload)
    logger.info("Travis Payload : %r.", json_payload)

    # get repo name from payload
    if ("repository" in json_payload and
            "owner_name" in json_payload["repository"] and
            "name" in json_payload["repository"]):

        repo = get_repo_slug(json_payload["repository"]["owner_name"],
                             json_payload["repository"]["name"])

        logger.info("Build repo : %s", repo)
        settings.set_project_name(repo)
        parameters["repo"] = repo

    # get build number from payload
    if "number" in json_payload:
        logger.info("Build number : %s", str(json_payload["number"]))
        settings.add_setting('build', json_payload['number'])
        parameters["build"] = json_payload['number']

    return parameters


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
    # get Travis account token from Settings
    token = Settings().get_setting("travis_account_token")

    # return True if token is not set
    if token is None:
        logger.info("Setting travis_account_token is not defined,"
                    " Travis CI notification Authorization header"
                    " is not checked.")
        return True

    # check if parameters are strings
    if is_string(repo) and is_string(auth_header) and is_string(token):
        # generate hash (encode string to bytes first)
        auth_hash = sha256((repo + token).encode('utf-8')).hexdigest()

        # compare hash with Authorization header
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
