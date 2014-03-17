#!/usr/bin/env python
# vim: set expandtab sw=4 ts=4:
# Reads timestamps.csv, calculates stage duration and saves the result
# to an xml file
# usage : analyse.py -h --build=<buildID= --job=<jobID> --branch=<branchname>
#
# Copyright (C) 2014 Dieter Adriaenssens
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

import csv
import os
import sys
import getopt
from lxml import etree

# use parameter for timestamps file and check if file exists
TIMESTAMP_FILE = os.getenv('BUILD_TREND_LOGFILE', 'timestamps.csv')
RESULT_FILE = os.getenv('BUILD_TREND_OUTPUTFILE', 'buildtimes.xml')
if not os.path.isfile(TIMESTAMP_FILE):
    quit()


def analyse(argv):
    # load previous builtimes file, or create a new xml root
    if os.path.isfile(RESULT_FILE):
        root_xml = etree.parse(RESULT_FILE).getroot()
    else:
        root_xml = etree.Element("builds")

    build_xml = etree.SubElement(root_xml, "build")

    # process arguments
    usage_string = 'analyse.py -h --build=<buildID=' \
        ' --job=<jobID> --branch=<branchname>'
    try:
        opts, args = getopt.getopt(
            argv, "h", ["build=", "job=", "branch=", "help"])
    except getopt.GetoptError:
        print usage_string
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', "--help"):
            print usage_string
            sys.exit()
        elif opt == "--build":
            build_xml.set("id", arg)
        elif opt == "--job":
            build_xml.set("job", arg)
        elif opt == "--branch":
            build_xml.set("branch", arg)

    # create stages element
    stages_xml = etree.SubElement(build_xml, "stages")

    # read timestamps, calculate stage duration and add it to xml tree
    with open(TIMESTAMP_FILE, 'rb') as csvfile:
        timestamps = csv.reader(csvfile, delimiter=',', quotechar='"')
        previous_timestamp = 0
        event_name = None
        for row in timestamps:
            if event_name is not None:
                if event_name == 'end':
                    break
                duration = int(row[1]) - previous_timestamp
                print 'Duration ' + event_name + ' : ' + str(duration) + 's'
                # add stage duration to xml tree
                stages_xml.append(etree.Element(
                    "stage", name=event_name, duration=str(duration)))
            event_name = row[0]
            previous_timestamp = int(row[1])

    # write xml to file
    with open(RESULT_FILE, 'wb') as xmlfile:
        xmlfile.write(etree.tostring(
            root_xml, xml_declaration=True,
            encoding='utf-8', pretty_print=True))

if __name__ == "__main__":
    analyse(sys.argv[1:])
