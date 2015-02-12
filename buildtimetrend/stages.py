# vim: set expandtab sw=4 ts=4:
"""
Build stage related classes.

Read timestamps.csv, calculates stage duration and saves the result
to an xml file.

Copyright (C) 2014-2015 Dieter Adriaenssens <ruleant@users.sourceforge.net>

This file is part of buildtimetrend/python-lib
<https://github.com/buildtimetrend/python-lib/>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

import csv
from buildtimetrend.tools import get_logger
from buildtimetrend.tools import split_timestamp
from buildtimetrend.tools import check_file
from buildtimetrend.tools import nano2sec
from lxml import etree


class Stages(object):

    """
    Build stages class.

    It gathers timestamps from a csv file and calculates stage duration.
    Output stages in xml format.
    """

    def __init__(self):
        """ Initialize instance. """
        self.stages = []
        self.started_at = None
        self.finished_at = None
        self.end_timestamp = 0

    def set_end_timestamp(self, timestamp):
        """
        Set end timestamp.

        Parameters:
        - timestamp : end timestamp
        """
        if type(timestamp) in (int, float) and timestamp > 0:
            get_logger().info("Set end_timestamp : %f", timestamp)
            self.end_timestamp = timestamp

    def read_csv(self, csv_filename):
        """
        Gather timestamps from a csv file and calculate stage duration.

        Parameters :
        - csv_filename : csv filename containing timestamps
        Returns false if file doesn't exist, true if it was read successfully.
        """
        # load timestamps file
        if not check_file(csv_filename):
            return False

        # read timestamps, calculate stage duration
        with open(csv_filename, 'r') as csv_data:
            timestamps = csv.reader(csv_data, delimiter=',', quotechar='"')
            self.parse_timestamps(timestamps)

        return True

    def total_duration(self):
        """ Calculate total duration of all stages. """
        total_duration = 0
        # calculate total duration
        for stage in self.stages:
            total_duration += stage["duration"]

        return total_duration

    def to_xml(self):
        """ Return xml object from stages dictionary. """
        root = etree.Element("stages")

        for stage in self.stages:
            root.append(etree.Element(
                "stage", name=stage["name"],
                duration=str(stage["duration"])))

        return root

    def to_xml_string(self):
        """ Return xml string from stages dictionary. """
        return etree.tostring(self.to_xml(), pretty_print=True)

    def parse_timestamps(self, timestamps):
        """
        Parse timestamps and calculate stage durations.

        The timestamp of each stage is used as both the start point of it's
        stage and the endpoint of the previous stage.
        On parsing each timestamp, the previous timestamp and previous
        event name are used to calculate the duration of the previous stage.
        For this reason, parsing the first timestamp line
        doesn't produce a stage duration.
        The parsing ends when an event with the name 'end' is encountered.
        """
        previous_timestamp = 0
        event_name = None

        # list of possible end tags
        end_tags = ['end', 'done', 'finished', 'completed']

        # iterate over all timestamps
        for row in timestamps:
            timestamp = float(row[1])

            # skip calculating the duration of the first stage,
            # the next timestamp is needed
            if event_name is not None:
                # finish parsing when an end timestamp is encountered
                if event_name.lower() in end_tags:
                    break

                self.create_stage(event_name, previous_timestamp, timestamp)

            # event name of the timestamp is used in the next iteration
            # the timestamp of the next stage is used as the ending timestamp
            # of this stage
            event_name = row[0]
            previous_timestamp = timestamp

        if self.end_timestamp > 0 and event_name.lower() not in end_tags:
            self.create_stage(event_name,
                              previous_timestamp,
                              self.end_timestamp)

    def add_stage(self, stage):
        """
        Add a stage.

        param stage Stage instance
        """
        if stage is None or type(stage) is not Stage:
            raise TypeError("param %s should be a Stage instance" % stage)

        # add stage
        self.stages.append(stage.to_dict())

        # assign starting timestamp of first stage
        # to started_at of the build job
        if self.started_at is None and "started_at" in stage.data:
            self.started_at = stage.data["started_at"]

        # assign finished timestamp
        if "finished_at" in stage.data:
            self.finished_at = stage.data["finished_at"]

    def create_stage(self, name, start_time, end_time):
        """
        Create and add a stage.

        Parameters :
        - name : stage name
        - start_time : start of stage timestamp
        - end_time : end of stage timestamp
        """
        # timestamps should be integer or floating point numbers
        if not (type(start_time) in (int, float) and
                type(end_time) in (int, float)):
            return None

        # calculate duration from start and end timestamp
        duration = end_time - start_time
        get_logger().info('Duration %s : %fs', name, duration)

        # create stage
        stage = Stage()
        stage.set_name(name)
        stage.set_started_at(start_time)
        stage.set_finished_at(end_time)
        stage.set_duration(duration)

        self.add_stage(stage)
        return stage


class Stage(object):

    """ Build stage object. """

    def __init__(self):
        """ Initialize instance. """
        self.data = {}
        self.set_name("")
        self.set_duration(0)

    def set_name(self, name):
        """ Set stage name. """
        if name is None:
            return False

        self.data["name"] = str(name)
        get_logger().info("Set name : %s", name)
        return True

    def set_command(self, command):
        """ Set stage command. """
        if command is None:
            return False

        self.data["command"] = str(command)
        return True

    def set_started_at(self, timestamp):
        """ Set time when stage was started. """
        return self.set_timestamp("started_at", timestamp)

    def set_started_at_nano(self, timestamp):
        """ Set time when stage was started in nanoseconds. """
        return self.set_timestamp_nano("started_at", timestamp)

    def set_finished_at(self, timestamp):
        """ Set time when stage was finished. """
        return self.set_timestamp("finished_at", timestamp)

    def set_finished_at_nano(self, timestamp):
        """ Set time when stage was finished in nanoseconds. """
        return self.set_timestamp_nano("finished_at", timestamp)

    def set_timestamp(self, name, timestamp):
        """
        Set timestamp.

        Parameters:
        - name timestamp name
        - timestamp seconds since epoch
        """
        if timestamp is not None and name is not None:
            try:
                self.data[name] = split_timestamp(timestamp)
                return True
            except TypeError:
                return False

        return False

    def set_timestamp_nano(self, name, timestamp):
        """
        Set timestamp in nanoseconds.

        Parameters:
        - name timestamp name
        - timestamp nanoseconds since epoch
        """
        return self.set_timestamp(name, nano2sec(timestamp))

    def set_duration(self, duration):
        """ Set stage duration in seconds. """
        try:
            duration = float(duration)
            if duration >= 0:
                self.data["duration"] = duration
                return True
            return False
        except (ValueError, TypeError):
            return False

    def set_duration_nano(self, duration):
        """ Set stage duration in nanoseconds. """
        try:
            return self.set_duration(nano2sec(duration))
        except (ValueError, TypeError):
            return False

    def to_dict(self):
        """ Return stages data as dictionary. """
        return self.data
