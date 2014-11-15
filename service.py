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

import sys
from buildtimetrend.travis import TravisData
from buildtimetrend.settings import Settings
from buildtimetrend.settings import process_argv
from buildtimetrend.keenio import log_build_keen
from buildtimetrend.keenio import keen_is_writable


def retrieve_and_store_data(argv):
    '''
    Retrieve timing data from Travis CI, parse it and store it in Keen.io
    '''

    settings = Settings()
    settings.load_config_file("config_service.yml")

    # process command line arguments
    process_argv(argv)

    build = settings.get_setting('build')
    if build is None:
        print "Build number is not set, use --build=build_id"
        return

    travis_data = TravisData(settings.get_project_name(), build)

    # retrieve build data using Travis CI API
    print "Retrieve build #%s data of %s from Travis CI" % \
        (build, settings.get_project_name())
    travis_data.get_build_data()

    # process all build jobs
    travis_data.process_build_jobs()

    if not keen_is_writable():
        print "Keen IO write key not set, no data was sent"
        return

    # send build job data to Keen.io
    for build_job in travis_data.build_jobs:
        print "Send build job #%s data to Keen.io" % build_job
        log_build_keen(travis_data.build_jobs[build_job])

if __name__ == "__main__":
    retrieve_and_store_data(sys.argv)
