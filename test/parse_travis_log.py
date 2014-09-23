#!/usr/bin/env python
# vim: set expandtab sw=4 ts=4:
#
# Parse Travis CI log file
#
# Copyright (C) 2014 Dieter Adriaenssens <ruleant@users.sourceforge.net>
#
# This file is part of buildtime-trend
# <https://github.com/ruleant/buildtime-trend/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from buildtimetrend.travis import TravisData

REPO = 'ruleant/buildtime-trend'
BUILD = '241'
LOGFILE = 'travis_log'

travis_data = TravisData(REPO, BUILD)

print "Build job log"
travis_data.parse_job_log_file(LOGFILE)

print
print "Finished stages"
for stage in travis_data.stages.stages:
    print "Substage %s, duration %ss, command : %s" % (stage["name"], stage["duration"], stage["command"])
