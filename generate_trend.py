#!/usr/bin/env python
# vim: set expandtab sw=4 ts=4:
#
# Generates a trend (graph) from the buildtimes in buildtimes.xml
#
# usage : generate_trend.py
#
# Copyright (C) 2014 Dieter Adriaenssens <ruleant@users.sourceforge.net>
#
# This file is part of buildtime-trend <https://github.com/ruleant/buildtime-trend/>
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
from lxml import etree

# use parameter for timestamps file and check if file exists
RESULT_FILE = os.getenv('BUILD_TREND_OUTPUTFILE', 'buildtimes.xml')
GRAPH_FILE = os.getenv('BUILD_TREND_TRENDFILE', 'trend.png')
if not os.path.isfile(RESULT_FILE):
    quit()


class Trend:
    def __init__(self):
        self.stages = {}
        self.builds = []

    def gather_data(self):
        # load builtimes file
        root_xml = etree.parse(RESULT_FILE).getroot()

        # print content of buildtimes file
        for build_xml in root_xml:
            build_summary = "Build ID : "
            if build_xml.get('id') is None:
                build_summary += "unknown"
                self.builds.append("#" + str(len(self.builds) + 1))
            else:
                build_summary += build_xml.get('id')
                build_summary += ", Job : "
                if build_xml.get('job') is None:
                    build_summary += "unknown"
                    self.builds.append("#" + str(len(self.builds) + 1))
                else:
                    build_summary += build_xml.get('job')
                    self.builds.append(build_xml.get('job'))
            for build_child in build_xml:
                if build_child.tag == 'stages':
                    build_summary += ", stages : " + str(len(build_child))
            print build_summary

    def generate(self):
        return None

if __name__ == "__main__":
    trend = Trend()
    trend.gather_data()
    # print number of builds and list of buildnames
    print "Builds (%d) :" % len(trend.builds), trend.builds
    trend.generate()
