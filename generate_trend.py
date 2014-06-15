#!/usr/bin/env python
# vim: set expandtab sw=4 ts=4:
#
# Generates a trend (graph) from the buildtimes in buildtimes.xml
#
# usage : generate_trend.py -h --trend=native
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

import os
import sys
import getopt


def generate_trend(argv):
    # process arguments
    usage_string = 'generate_trend.py -h --trend=native'
    try:
        opts, args = getopt.getopt(argv, "h", ["trend=", "help"])
    except getopt.GetoptError:
        print usage_string
        sys.exit(2)

    #check options
    for opt, arg in opts:
        if opt in ('-h', "--help"):
            print usage_string
            sys.exit()
        elif opt == "--trend":
            if arg == "native":
                trend_native()

    # run trend_keen() always,
    # if $KEEN_PROJECT_ID variable is set (checked later), it will be executed
    trend_keen()


def trend_native():
    from buildtimetrend.trend import Trend
    # use parameter for timestamps file and check if file exists
    result_file = os.getenv('BUILD_TREND_OUTPUTFILE', 'trends/buildtimes.xml')
    chart_file = os.getenv('BUILD_TREND_TRENDFILE', 'trends/trend.png')

    trend = Trend()
    if trend.gather_data(result_file):
        # print number of builds and list of buildnames
        print 'Builds ({}) :'.format(len(trend.builds)), trend.builds
        print 'Stages ({}) :'.format(len(trend.stages)), trend.stages
        trend.generate(chart_file)


def trend_keen():
    from buildtimetrend.keenio import generate_overview_config_file

    # TODO use generic repo value (create general config object)
    if 'TRAVIS_REPO_SLUG' in os.environ:
        generate_overview_config_file(os.getenv('TRAVIS_REPO_SLUG'))

if __name__ == "__main__":
    generate_trend(sys.argv[1:])
