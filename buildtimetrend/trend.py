# vim: set expandtab sw=4 ts=4:
#
# Generates a trend (graph) from the buildtimes in buildtimes.xml
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
from lxml import etree
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
from matplotlib import pyplot as plt


class Trend(object):
    def __init__(self):
        self.stages = {}
        self.builds = []

    def gather_data(self, result_file):
        # load builtimes file
        if os.path.isfile(result_file):
            root_xml = etree.parse(result_file).getroot()
        else:
            print "File doesn't exist : %s" % result_file
            return False

        index = 0
        # print content of buildtimes file
        for build_xml in root_xml:
            build_id = "#%d" % (index + 1)
            build_summary = "Build ID : "
            if build_xml.get('id') is None:
                build_summary += "unknown"
            else:
                build_summary += build_xml.get('id')
                build_summary += ", Job : "
                if build_xml.get('job') is None:
                    build_id = build_xml.get('id')
                    build_summary += "unknown"
                else:
                    build_summary += build_xml.get('job')
                    build_id = build_xml.get('job')

            self.builds.append(build_id)

            # add 0 to each existing stage, to make sure that
            # the indexes of each value
            # are correct, even if a stage does not exist in a build
            # if a stage exists, the zero will be replaced by its duration
            for stage in self.stages:
                self.stages[stage].append(0)

            # add duration of each stage to stages list
            for build_child in build_xml:
                if build_child.tag == 'stages':
                    build_summary += ", stages : " + str(len(build_child))
                    for stage in build_child:
                        if (stage.tag == 'stage' and
                                stage.get('name') is not None and
                                stage.get('duration') is not None):
                            if stage.get('name') in self.stages:
                                temp_dict = self.stages[stage.get('name')]
                            else:
                                # when a new stage is added,
                                # create list with zeros,
                                # one for each existing build
                                temp_dict = [0]*(index + 1)
                            temp_dict[index] = int(stage.get('duration'))
                            self.stages[stage.get('name')] = temp_dict
            print build_summary
            index += 1
        return True

    def generate(self, trend_file):
        fig, axes = plt.subplots()

        # add data
        x = range(len(self.builds))
        plots = axes.stackplot(x, self.stages.values())
        plt.xticks(x, self.builds, rotation=45)

        # label axes and add graph title
        axes.set_xlabel("Builds", {'fontsize': 14})
        axes.set_ylabel("Duration [s]", {'fontsize': 14})
        axes.set_title("Build stages trend", {'fontsize': 22})

        # display legend
        legend_proxies = []
        for plot in plots:
            legend_proxies.append(
                plt.Rectangle((0, 0), 1, 1, fc=plot.get_facecolor()[0]))
        # add legend in reverse order
        axes.legend(legend_proxies[::-1], self.stages.keys()[::-1], loc=7)

        # save figure
        plt.savefig(trend_file)
