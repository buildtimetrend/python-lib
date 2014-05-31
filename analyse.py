#!/usr/bin/env python
# vim: set expandtab sw=4 ts=4:
# Reads timestamps.csv, calculates stage duration and saves the result
# to an xml file
# usage :
#  analyse.py -h
#    --build=<buildID>
#    --job=<jobID>
#    --branch=<branchname>
#    --repo=<repo_slug>
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
from lxml import etree
import keen
from buildtimetrend.build import Build
from buildtimetrend.keenio import keen_io_writable

# use parameter for timestamps file and check if file exists
TIMESTAMP_FILE = os.getenv('BUILD_TREND_LOGFILE', 'timestamps.csv')
RESULT_FILE = os.getenv('BUILD_TREND_OUTPUTFILE', 'buildtimes.xml')
if not os.path.isfile(TIMESTAMP_FILE):
    quit()


def analyse(argv):
    # load previous buildtimes file, or create a new xml root
    if os.path.isfile(RESULT_FILE):
        root_xml = etree.parse(RESULT_FILE).getroot()
    else:
        root_xml = etree.Element("builds")

    # read build data from timestamp CSV file
    build = Build(TIMESTAMP_FILE)

    # process arguments
    usage_string = 'analyse.py -h --build=<buildID>' \
        ' --job=<jobID> --branch=<branchname> --repo=<repo_slug>'
    try:
        opts, args = getopt.getopt(
            argv, "h", ["build=", "job=", "branch=", "repo=", "help"])
    except getopt.GetoptError:
        print usage_string
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', "--help"):
            print usage_string
            sys.exit()
        elif opt == "--build":
            build.add_property("build", arg)
        elif opt == "--job":
            build.add_property("job", arg)
        elif opt == "--branch":
            build.add_property("branch", arg)
        elif opt == "--repo":
            build.add_property("repo", arg)

    # send build data to keen.io
    if keen_io_writable():
        keen.add_event("builds", build.to_dict())

    # add build data to xml
    root_xml.append(build.to_xml())

    # write xml to file
    with open(RESULT_FILE, 'wb') as xmlfile:
        xmlfile.write(etree.tostring(
            root_xml, xml_declaration=True,
            encoding='utf-8', pretty_print=True))

if __name__ == "__main__":
    analyse(sys.argv[1:])
