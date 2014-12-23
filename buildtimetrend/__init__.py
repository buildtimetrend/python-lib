'''
Buildtime Trend : Gather data, analyse and visualise trends of build processes
on Continuous Integration platforms

Buildtime trend library, to parse input files with timestamps,
analyse them, store the results and other supporting tools.

Copyright (C) 2014 Dieter Adriaenssens <ruleant@users.sourceforge.net>

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
'''
from buildtimetrend.tools import set_loglevel

NAME = "buildtimetrend"
VERSION = "0.2-dev"
SCHEMA_VERSION = "2"
USER_AGENT = "%s/%s" % (NAME, VERSION)


set_loglevel("WARNING")
