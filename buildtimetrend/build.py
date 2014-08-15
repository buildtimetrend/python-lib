'''
vim: set expandtab sw=4 ts=4:

Gathers build related data.

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

import copy
from lxml import etree
from buildtimetrend.stages import Stages
from buildtimetrend.tools import split_isotimestamp


class Build(object):
    '''
    Gathers Build related data.
    '''

    def __init__(self, csv_filename=None):
        self.properties = {}
        self.stages = Stages()
        if csv_filename is not None:
            self.stages.read_csv(csv_filename)

    def add_stages(self, stages):
        '''
        Add a Stages instance

        Parameters :
        - stages : Stages instance
        '''
        if stages is not None and type(stages) is Stages:
            self.stages = stages

    def add_property(self, name, value):
        '''
        Add a build property

        Parameters :
        - name : Property name
        - value : Property value
        '''
        self.properties[name] = value

    def get_property(self, name):
        '''
        Add a build property

        Parameters :
        - name : Property name
        '''
        if name in self.properties:
            return self.properties[name]

    def get_properties(self):
        '''
        Return build properties
        '''
        # copy values of properties
        data = copy.deepcopy(self.properties)

        # add total duration
        data["duration"] = self.stages.total_duration()

        # add started_at of first stage if it is defined
        # and if it is not set in properties
        if self.stages.started_at is not None and "started_at" not in data:
            data["started_at"] = self.stages.started_at

        # add finished_at of last stage if it is defined
        # and if it is not set in properties
        if self.stages.finished_at is not None and "finished_at" not in data:
            data["finished_at"] = self.stages.finished_at

        return data

    def set_started_at(self, isotimestamp):
        '''
        Set timestamp when build started.

        Parameters :
        - isotimestamp : timestamp in iso format when build started
        '''
        self.add_property("started_at", split_isotimestamp(isotimestamp))

    def set_finished_at(self, isotimestamp):
        '''
        Set timestamp when build finished.

        Parameters :
        - isotimestamp : timestamp in iso format when build started
        '''
        self.add_property("finished_at", split_isotimestamp(isotimestamp))

    def to_dict(self):
        '''
        Return object as dictionary
        '''
        # get build properties
        data = self.get_properties()

        # add stages
        if type(self.stages) is Stages:
            data["stages"] = self.stages.stages

        return data

    def stages_to_list(self):
        '''
        Return list of stages, all containing the build properties
        '''
        if type(self.stages) is Stages:
            # create list to be returned
            data = []

            # get build properties
            build_properties = self.get_properties()

            # iterate all stages
            for stage in self.stages.stages:
                temp = {}
                # copy stage data
                temp["stage"] = copy.deepcopy(stage)
                # copy values of properties
                if len(build_properties) > 0:
                    temp["build"] = build_properties
                data.append(temp)

        return data

    def to_xml(self):
        '''Generates xml object of Build instance'''
        root = etree.Element("build")

        # add properties
        for key in self.properties:
            root.set(str(key), str(self.properties[key]))

        # add stages
        if type(self.stages) is Stages:
            root.append(self.stages.to_xml())

        return root

    def to_xml_string(self):
        '''Generates xml string of Build instance'''
        return etree.tostring(self.to_xml(), pretty_print=True)
