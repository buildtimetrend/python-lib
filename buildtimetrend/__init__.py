"""
Buildtime Trend python library.

Features :
- parse input files with timestamps,
- retrieve and parse Travis CI build logfiles
- analyse the data
- store the results in XML format or Keen.io database
- other supporting tools

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
import logging

NAME = "buildtimetrend"
VERSION = "0.3"
SCHEMA_VERSION = "3"
USER_AGENT = "%s/%s" % (NAME, VERSION)


def get_logger():
    """Return logger object."""
    return logging.getLogger(NAME)


def set_loglevel(loglevel):
    """
    Set loglevel.

    Based on example on https://docs.python.org/2/howto/logging.html

    Assuming loglevel is bound to the string value obtained from the
    command line argument. Convert to upper case to allow the user to
    specify --log=DEBUG or --log=debug
    """
    if loglevel is None or type(loglevel) is not str:
        raise TypeError("param %s should be a string" % 'loglevel')

    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)

    # create handler
    log_handler = logging.StreamHandler()
    log_handler.setLevel(numeric_level)

    # remove default log handlers
    logger.handlers = []

    # setup logger
    logger.setLevel(numeric_level)
    logger.addHandler(log_handler)
    logger.info("Set loglevel to %s (%d)", loglevel.upper(), numeric_level)


logger = get_logger()
set_loglevel("WARNING")
