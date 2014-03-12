#!/usr/bin/env python
# vim: set expandtab sw=4 ts=4:
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
from lxml import etree

# use parameter for timestamps file and check if file exists
timestamp_file = os.getenv('BUILD_TREND_LOGFILE', 'timestamps.csv')
if not os.path.isfile(timestamp_file):
    quit()

# create xml root tag
build_xml = etree.Element("build")
stages_xml = etree.SubElement(build_xml, "stages")

with open(timestamp_file, 'rb') as csvfile:
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
            stages_xml.append(etree.Element("stage", name=event_name,
                duration=str(duration)))
        event_name = row[0]
        previous_timestamp = int(row[1])

print etree.tostring(build_xml, pretty_print=True)
