#!/usr/bin/env python
# vim: set expandtab sw=4 ts=4:
'''
Reads timestamps.csv, calculates stage duration and saves the result
to an xml file or sends it to Keen.io, depending on the mode.

Usage :
  analyse.py -h
    --log=<log_level> : DEBUG, INFO, WARNING, ERRROR, CRITICAL
    --build=<buildID>
    --job=<jobID>
    --branch=<branchname>
    --repo=<repo_slug>
    --ci=<ci_platform> : fe. travis, jenkins, shippable, local, ...
    --result=<build_result> : fe. passed, failed, errored, ...
    --mode=<storage_mode> : fe. native, keen (default)

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

import os
import sys
from buildtimetrend.settings import Settings
from buildtimetrend.settings import process_argv
from buildtimetrend.build import Build
from buildtimetrend.travis import TravisData
from buildtimetrend.travis import load_travis_env_vars
from buildtimetrend.keenio import log_build_keen
from buildtimetrend.tools import check_file
from buildtimetrend.tools import get_logger

# use parameter for timestamps file and check if file exists
TIMESTAMP_FILE = os.getenv('BUILD_TREND_LOGFILE', 'timestamps.csv')
RESULT_FILE = os.getenv('BUILD_TREND_OUTPUTFILE', 'buildtimes.xml')


def analyse(argv):
    '''
    Analyse timestamp file
    '''
    settings = Settings()

    # load Travis environment variables and save them in settings
    load_travis_env_vars()

    # process command line arguments
    process_argv(argv)

    # read build data from timestamp CSV file
    build = Build(TIMESTAMP_FILE)

    # load build properties from settings
    build.load_properties_from_settings()

    # retrieve data from Travis CI API
    if build.get_property("ci_platform") == "travis":
        travis_data = TravisData(
            build.get_property("repo"),
            build.get_property("build"),
        )
        travis_data.get_build_data()
        build.set_started_at(travis_data.get_started_at())

    # log data
    if settings.get_setting("mode_native") is True:
        log_build_native(build)
    if settings.get_setting("mode_keen") is True:
        log_build_keen(build)


def log_build_native(build):
    '''Store build data in xml format'''
    # import dependency
    from lxml import etree

    # load previous buildtimes file, or create a new xml root
    if check_file(RESULT_FILE):
        try:
            root_xml = etree.parse(RESULT_FILE).getroot()
        except etree.XMLSyntaxError:
            get_logger().error('XML format invalid : a new file is created,'
                               ' corrupt file is discarded')
            root_xml = etree.Element("builds")
    else:
        root_xml = etree.Element("builds")

    # add build data to xml
    root_xml.append(build.to_xml())

    # write xml to file
    with open(RESULT_FILE, 'wb') as xmlfile:
        xmlfile.write(etree.tostring(
            root_xml, xml_declaration=True,
            encoding='utf-8', pretty_print=True))


if __name__ == "__main__":
    # only run analysis if timestampfile is present
    if check_file(TIMESTAMP_FILE):
        analyse(sys.argv)
