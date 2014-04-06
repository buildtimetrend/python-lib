# vim: set expandtab sw=4 ts=4:
#
# Unit tests for Trend class
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

from buildtimetrend.build import Build
from lxml import etree
import unittest

TEST_SAMPLE_FILE = 'test/testsample_timestamps.csv'


class TestBuild(unittest.TestCase):
    def setUp(self):
        self.build = Build()

    def test_novalue(self):
        # number of stages should be zero
        self.assertEquals(0, len(self.build.stages.stages))

        # dict should be empty
        self.assertDictEqual({'stages' : {}}, self.build.to_dict())

        # xml shouldn't contain items
        self.assertEquals(
            '<build><stages/></build>', etree.tostring(self.build.to_xml()))
        self.assertEquals(
            '<build>\n'
            '  <stages/>\n'
            '</build>\n', self.build.to_xml_string())

    def test_nofile(self):
        # number of stages should be zero when file doesn't exist
        self.build = Build('nofile.csv')
        self.assertEquals(0, len(self.build.stages.stages))

        self.build = Build('')
        self.assertEquals(0, len(self.build.stages.stages))

    def test_to_dict(self):
        # read and parse sample file
        self.build = Build(TEST_SAMPLE_FILE)

        # test dict
        self.assertDictEqual(
            {'stages': {'stage1': 2, 'stage2': 5, 'stage3': 10}},
            self.build.to_dict())

    def test_to_xml(self):
        # read and parse sample file
        self.build = Build(TEST_SAMPLE_FILE)

        # test xml output
        self.assertEquals(
            '<build><stages><stage duration="2" name="stage1"/>'
            '<stage duration="5" name="stage2"/>'
            '<stage duration="10" name="stage3"/></stages></build>',
            etree.tostring(self.build.to_xml()))

    def test_to_xml_string(self):
        # read and parse sample file
        self.build = Build(TEST_SAMPLE_FILE)

        # test xml string output
        self.assertEquals(
            '<build>\n'
            '  <stages>\n'
            '    <stage duration="2" name="stage1"/>\n'
            '    <stage duration="5" name="stage2"/>\n'
            '    <stage duration="10" name="stage3"/>\n'
            '  </stages>\n'
            '</build>\n',
            self.build.to_xml_string())
