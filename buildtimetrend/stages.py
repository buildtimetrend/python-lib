# vim: set expandtab sw=4 ts=4:
'''
Reads timestamps.csv, calculates stage duration and saves the result
to an xml file

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

import csv
from buildtimetrend.tools import split_timestamp
from buildtimetrend.tools import check_file
from lxml import etree


class Stages(object):
    '''
    Build stages object.
    It gathers timestamps from a csv file and calculates stage duration.
    Output stages in xml format.
    '''

    def __init__(self):
        self.stages = []
        self.started_at = None
        self.finished_at = None

    def read_csv(self, csv_filename):
        '''
        Gathers timestamps from a csv file and calculates stage duration.

        Parameters :
        - csv_filename : csv filename containing timestamps
        Returns false if file doesn't exist, true if it was read successfully.
        '''
        # load timestamps file
        if not check_file(csv_filename):
            return False

        # read timestamps, calculate stage duration
        with open(csv_filename, 'rb') as csv_data:
            timestamps = csv.reader(csv_data, delimiter=',', quotechar='"')
            self.parse_timestamps(timestamps)

        return True

    def total_duration(self):
        '''Calculate total duration of all stages'''
        total_duration = 0
        # calculate total duration
        for stage in self.stages:
            total_duration += stage["duration"]

        return total_duration

    def to_xml(self):
        '''Generates xml object from stages dictionary'''
        root = etree.Element("stages")

        for stage in self.stages:
            root.append(etree.Element(
                "stage", name=stage["name"],
                duration=str(stage["duration"])))

        return root

    def to_xml_string(self):
        '''Generates xml string from stages dictionary'''
        return etree.tostring(self.to_xml(), pretty_print=True)

    def parse_timestamps(self, timestamps):
        '''
        Parse timestamps and calculate stage durations

        The timestamp of each stage is used as both the start point of it's
        stage and the endpoint of the previous stage.
        On parsing each timestamp, the previous timestamp and previous
        event name are used to calculate the duration of the previous stage.
        For this reason, parsing the first timestamp line
        doesn't produce a stage duration.
        The parsing ends when an event with the name 'end' is encountered.
        '''
        previous_timestamp = 0
        event_name = None
        # iterate over all timestamps
        for row in timestamps:
            timestamp = int(row[1])

            # list of possible end tags
            end_tags = ['end', 'done', 'finished', 'completed']

            # assign starting timestamp of first stage
            # to started_at of the build job
            if self.started_at is None:
                self.started_at = split_timestamp(timestamp)

            # skip calculating the duration of the first stage,
            # the next timestamp is needed
            if event_name is not None:
                # finish parsing when an end timestamp is encountered
                if event_name.lower() in end_tags:
                    self.finished_at = split_timestamp(previous_timestamp)
                    break

                # calculate duration from current and previous timestamp
                duration = timestamp - previous_timestamp
                print 'Duration {0} : {1}s'.format(event_name, duration)

                # add stage duration to stages dict
                self.stages.append({
                    "name": event_name,
                    "started_at": split_timestamp(previous_timestamp),
                    "finished_at": split_timestamp(timestamp),
                    "duration": duration})

            # event name of the timestamp is used in the next iteration
            # the timestamp of the next stage is used as the ending timestamp
            # of this stage
            event_name = row[0]
            previous_timestamp = timestamp


class Stage(object):
    '''
    Build stage object.
    '''

    def __init__(self):
        self.data = {}
        self.set_name("")
        self.set_duration(0)

    def set_name(self, name):
        '''Set stage name'''
        if name is None:
            return False

        self.data["name"] = str(name)
        return True

    def set_command(self, command):
        '''Set stage command'''
        if command is None:
            return False

        self.data["command"] = str(command)
        return True

    def set_started_at(self, timestamp):
        '''Set time when stage was started'''
        return self.set_timestamp("started_at", timestamp)

    def set_finished_at(self, timestamp):
        '''Set time when stage was finished'''
        return self.set_timestamp("finished_at", timestamp)

    def set_timestamp(self, name, timestamp):
        '''
        Set timestamp
        Param name timestamp name
        Param timestamp seconds since epoch
        '''
        if timestamp is not None and name is not None:
            try:
                self.data[name] = split_timestamp(timestamp)
                return True
            except TypeError:
                return False

        return False

    def set_timestamp_nano(self, name, timestamp):
        '''
        Set timestamp in nanoseconds
        Param name timestamp name
        Param timestamp nanoseconds since epoch
        '''
        return self.set_timestamp(name, timestamp / float(1000000000))

    def set_duration(self, duration):
        '''Set stage duration in seconds'''
        try:
            duration = float(duration)
            if duration >= 0:
                self.data["duration"] = duration
                return True
            return False
        except (ValueError, TypeError):
            return False

    def to_dict(self):
        '''return stages data as dictionary'''
        return self.data
