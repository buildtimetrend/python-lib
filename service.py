#!/usr/bin/env python
# vim: set expandtab sw=4 ts=4:
'''
Retrieve Travis CI build data and log to Keen.io

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

from buildtimetrend.travis import TravisData
from buildtimetrend.settings import Settings
from buildtimetrend.keenio import log_build_keen

REPO = 'ruleant/buildtime-trend'
BUILD = ''

Settings().set_project_name(REPO)

travis_data = TravisData(REPO, BUILD)

# retrieve build data using Travis CI API
print "Retrieve build #%s data from Travis CI" % BUILD
travis_data.get_build_data()

# process all build jobs
travis_data.process_build_jobs()

# send build job data to Keen.io
for build_job in travis_data.build_jobs:
    print "Send build job #%s data to Keen.io" % build_job
    log_build_keen(travis_data.build_jobs[build_job])
