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


def generate_trend():
    # load builtimes file
    root_xml = etree.parse(RESULT_FILE).getroot()

    # print number of builds in buildtimes file
    print("Number of builds : " + str(len(root_xml)))

    # print content of buildtimes file
    for build_xml in root_xml:
        build_summary = "Build ID : "
        if build_xml.get('id') is None:
            build_summary += " unknown"
        else:
            build_summary += build_xml.get('id')
            build_summary += ", Job : " + build_xml.get('job')
        print build_summary
        for build_child in build_xml:
            if build_child.tag == 'stages':
                print ("Stages : " + str(len(build_child)))
        print("")

if __name__ == "__main__":
    generate_trend()
