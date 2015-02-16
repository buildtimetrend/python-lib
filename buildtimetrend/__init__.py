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
from buildtimetrend.tools import set_loglevel

NAME = "buildtimetrend"
VERSION = "0.2"
SCHEMA_VERSION = "2"
USER_AGENT = "%s/%s" % (NAME, VERSION)


set_loglevel("WARNING")
