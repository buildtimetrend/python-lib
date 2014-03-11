#!/usr/bin/env python
# vim: set expandtab sw=4 ts=4:
import csv
import os
# use parameter for timestamps file and check if file exists
timestamp_file = os.getenv('BUILD_TREND_LOGFILE', 'timestamps.csv')
if not os.path.isfile(timestamp_file):
    quit()

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
        event_name = row[0]
        previous_timestamp = int(row[1])
