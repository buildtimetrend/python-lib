'''
Buildtime Trend : Gather data, analyse and visualise trends of build processes
on Continuous Integration platforms

Buildtime trend library, to parse input files with timestamps,
analyse them, store the results and other supporting tools.

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
import logging

VERSION = "0.2-dev"
SCHEMA_VERSION = "2"
USER_AGENT = "buildtime-trend/" + VERSION


def set_loglevel(loglevel):
    '''
    Sets loglevel
    Based on example on https://docs.python.org/2/howto/logging.html

    Assuming loglevel is bound to the string value obtained from the
    command line argument. Convert to upper case to allow the user to
    specify --log=DEBUG or --log=debug
    '''
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % loglevel)
    #logging.basicConfig(level=numeric_level)
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
