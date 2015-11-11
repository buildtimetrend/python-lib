# vim: set expandtab sw=4 ts=4:
"""
Service related methods.

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

from __future__ import division
import cgi
from buildtimetrend import logger
from buildtimetrend.settings import Settings
from buildtimetrend.keenio import has_build_id
from buildtimetrend.keenio import keen_is_writable


def is_repo_allowed(repo):
    """
    Check if repo is allowed.

    A repository name is checked against a list of denied and allowed repos.
    The 'denied_repo' check takes precendence over 'allowed_repo' check.
    The list of denied/allowed repos is defined with settings 'denied_repo'
    and 'allowed_repo'.
    If the settings are not defined,
    the repo is not checked against the denied/allowed lists.
    Both 'denied_repo' and 'allowed_repo' can have multiple values,
    if any of them matches a substring of the repo, the repo is denied/allowed.

    Parameters:
    -repo : repository name
    """
    if repo is None:
        logger.warning("Repo is not defined")
        return False

    denied_message = "Project '%s' is not allowed."
    denied_repo = Settings().get_setting("denied_repo")
    allowed_repo = Settings().get_setting("allowed_repo")

    if denied_repo is not None and \
            any(x in repo for x in denied_repo) or \
            allowed_repo is not None and \
            not any(x in repo for x in allowed_repo):
        logger.warning(denied_message, repo)
        return False

    return True


def format_duration(duration):
    """
    Format duration from seconds to hours, minutes and seconds.

    Parameters:
    - duration : duration in seconds
    """
    if type(duration) not in (float, int) or duration < 0:
        return "unknown"

    # round duration
    duration = round(duration)

    seconds = int(duration % 60)
    duration = duration / 60
    format_string = "{:d}s".format(seconds)

    if duration >= 1:
        minutes = int(duration % 60)
        duration = duration / 60
        format_string = "{:d}m {:s}".format(minutes, format_string)

        if duration >= 1:
            hours = int(duration % 60)
            format_string = "{:d}h {:s}".format(hours, format_string)

    return format_string


def check_process_parameters(repo=None, build=None):
    """
    Process setup parameters.

    Deprecated : functionality is split into
    validate_travis_request() and validate_task_parameters()

    Check parameters (repo and build)
    Returns error message, None when all parameters are fine
    """
    ret_val = validate_travis_request(repo, build)
    if ret_val is not None:
        return ret_val
    return validate_task_parameters(repo, build)


def validate_travis_request(repo=None, build=None):
    """
    Validate repo and build parameters of travis web request.

    Check parameters (repo and build)
    Returns error message, None when all parameters are fine.
    """
    if repo is None or build is None:
        logger.warning("Repo or build number are not set")
        return "Repo or build are not set, format : " \
            "/travis/<repo_owner>/<repo_name>/<build>"

    # check if repo is allowed
    if not is_repo_allowed(repo):
        return "Project '%s' is not allowed." % cgi.escape(repo)

    return None


def validate_task_parameters(repo=None, build=None):
    """
    Validate repo and build parameters of process_travis_buildlog().

    Check parameters (repo and build)
    Returns error message, None when all parameters are fine.
    """
    if not keen_is_writable():
        return "Keen IO write key not set, no data was sent"

    try:
        if has_build_id(repo, build):
            return "Build #%s of project %s already exists in database" % \
                (cgi.escape(build), cgi.escape(repo))
    except Exception as msg:
        # Raise last exception again
        logger.error("Error checking if build exists : %s", msg)
        raise SystemError("Error checking if build exists.")

    return None
