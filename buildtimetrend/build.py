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

    def to_dict(self):
        '''
        Return object as dictionary
        '''
        # copy values of properties
        data = copy.deepcopy(self.properties)

        # add stages
        if type(self.stages) is Stages:
            data["stages"] = self.stages.stages

        return data

    def stages_to_list(self):
        '''
        Return list of stages, all containing the build properties
        '''
        if type(self.stages) is Stages:
            # copy values of stages
            data = copy.deepcopy(self.stages.stages)

            # add build properties
            for stage in data:
                # copy values of properties
                if len(self.properties) > 0:
                    stage["build"] = copy.deepcopy(self.properties)

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
