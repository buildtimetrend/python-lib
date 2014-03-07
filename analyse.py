#!/usr/bin/env python
import csv
# TODO use parameter for timestamps file and check if file exists
with open('timestamps.csv', 'rb') as csvfile:
    timestamps = csv.reader(csvfile, delimiter=',', quotechar='"')
    previousTime = 0
    eventName = None
    for row in timestamps:
	if eventName is not None:
	    if eventName == 'end':
                break
	    duration = int(row[1]) - previousTime
	    print 'Duration ' + eventName + ' : ' + str(duration) + 's'
	eventName = row[0]
	previousTime = int(row[1])
