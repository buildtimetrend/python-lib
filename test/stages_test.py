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

from buildtimetrend.stages import Stages
from lxml import etree
import unittest

TEST_SAMPLE_FILE = 'test/testsample_timestamps.csv'


class TestTimestamps(unittest.TestCase):
    def setUp(self):
        self.stages = Stages()

    def test_novalue(self):
        # number of stages should be zero
        self.assertEquals(0, len(self.stages.stages))
        # xml shouldn't contain items
        self.assertEquals("<stages/>", etree.tostring(self.stages.to_xml()))
        self.assertEquals("<stages/>\n", self.stages.to_xml_string())

    def test_nofile(self):
        # function should return false when file doesn't exist
        self.assertFalse(self.stages.read_csv('nofile.csv'))
        self.assertFalse(self.stages.read_csv(''))

        # function should thrown an error  when no filename is set
        self.assertRaises(TypeError, self.stages.read_csv)

    def test_read_csv(self):
        # read and parse sample file
        self.assertTrue(self.stages.read_csv(TEST_SAMPLE_FILE))

        # test number of stages
        self.assertEquals(3, len(self.stages.stages))

        # test stages (names + duration)
        self.assertDictEqual(
            {'stage1': {'duration': 2, 'name': 'stage1'},
            'stage2': {'duration': 5, 'name': 'stage2'},
            'stage3': {'duration': 10, 'name': 'stage3'}},
            self.stages.stages)

    def test_to_xml(self):
        # read and parse sample file
        self.stages.read_csv(TEST_SAMPLE_FILE)

        # test xml output
        self.assertEquals(
            '<stages><stage duration="2" name="stage1"/>'
            '<stage duration="5" name="stage2"/>'
            '<stage duration="10" name="stage3"/></stages>',
            etree.tostring(self.stages.to_xml()))

    def test_to_xml_string(self):
        # read and parse sample file
        self.stages.read_csv(TEST_SAMPLE_FILE)

        # test xml string output
        self.assertEquals(
            '<stages>\n'
            '  <stage duration="2" name="stage1"/>\n'
            '  <stage duration="5" name="stage2"/>\n'
            '  <stage duration="10" name="stage3"/>\n'
            '</stages>\n',
            self.stages.to_xml_string())
