# vim: set expandtab sw=4 ts=4:
# disable pylint message about unused variable 'fig'
# pylint: disable=unused-variable
"""
Generate a chart from the gathered buildtime data.

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

from lxml import etree
from buildtimetrend.tools import get_logger
from buildtimetrend.tools import check_file
import matplotlib
# Force matplotlib to not use any Xwindow backend.
matplotlib.use('Agg')
from matplotlib import pyplot as plt


class Trend(object):

    """ Trend class, generate a chart from gathered buildtime data. """

    def __init__(self):
        """ Initialize instance. """
        self.stages = {}
        self.builds = []

    def gather_data(self, result_file):
        """
        Get buildtime data from an xml file.

        Parameters
        - result_file : xml file containing the buildtime data
        """
        # load buildtimes file
        if check_file(result_file):
            root_xml = etree.parse(result_file).getroot()
        else:
            return False

        index = 0
        # print content of buildtimes file
        for build_xml in root_xml:
            build_id = build_xml.get('build')
            job_id = build_xml.get('job')

            if job_id is None and build_id is None:
                build_name = "#%d" % (index + 1)
            elif job_id is not None:
                build_name = job_id
            else:
                build_name = build_id

            self.builds.append(build_name)

            # add 0 to each existing stage, to make sure that
            # the indexes of each value
            # are correct, even if a stage does not exist in a build
            # if a stage exists, the zero will be replaced by its duration
            for stage in self.stages:
                self.stages[stage].append(0)

            # add duration of each stage to stages list
            for build_child in build_xml:
                if build_child.tag == 'stages':
                    stage_count = len(build_child)
                    self.parse_xml_stages(build_child, index)
            get_logger().debug("Build ID : %s, Job : %s, stages : %d",
                               build_id, job_id, stage_count)
            index += 1
        return True

    def parse_xml_stages(self, stages, index):
        """ Parse stages in from xml file. """
        for stage in stages:
            if (stage.tag == 'stage' and
                    stage.get('name') is not None and
                    stage.get('duration') is not None):
                if stage.get('name') in self.stages:
                    temp_dict = self.stages[stage.get('name')]
                else:
                    # when a new stage is added,
                    # create list with zeros,
                    # one for each existing build
                    temp_dict = [0] * (index + 1)
                temp_dict[index] = float(stage.get('duration'))
                self.stages[stage.get('name')] = temp_dict

    def generate(self, trend_file):
        """
        Generate the trend chart and save it as a PNG image using matplotlib.

        Parameters
        - trend_file : file name to save chart image to
        """
        fig, axes = plt.subplots()

        # add data
        x_values = range(len(self.builds))
        plots = plt.stackplot(x_values, self.stages.values())
        plt.xticks(x_values, self.builds, rotation=45, size=10)

        # label axes and add graph title
        axes.set_xlabel("Builds", {'fontsize': 14})
        axes.xaxis.set_label_coords(1.05, -0.05)
        axes.set_ylabel("Duration [s]", {'fontsize': 14})
        axes.set_title("Build stages trend", {'fontsize': 22})

        # display legend
        legend_proxies = []
        for plot in plots:
            legend_proxies.append(
                plt.Rectangle((0, 0), 1, 1, fc=plot.get_facecolor()[0]))
        # add legend in reverse order, in upper left corner
        axes.legend(legend_proxies[::-1], self.stages.keys()[::-1], loc=2)

        # save figure
        plt.savefig(trend_file)
