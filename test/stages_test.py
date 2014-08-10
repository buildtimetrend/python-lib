# vim: set expandtab sw=4 ts=4:
#
# Unit tests for Stages class
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

TEST_SAMPLE_FILE = 'test/testsample_timestamps_done.csv'
STAGES_RESULT = [{'duration': 17,
             'finished_at': '2014-04-01T18:59:12',
             'name': 'stage1',
             'started_at': '2014-04-01T18:58:55'}]


class TestStages(unittest.TestCase):
    def setUp(self):
        self.stages = Stages()
        # show full diff in case of assert mismatch
        self.maxDiff = None

    def test_novalue(self):
        # number of stages should be zero
        self.assertEquals(0, len(self.stages.stages))
        # test total duration
        self.assertEqual(0, self.stages.total_duration())
        # test started_at and finished_at
        self.assertEqual(None, self.stages.started_at)
        self.assertEqual(None, self.stages.finished_at)
        # xml shouldn't contain items
        self.assertEquals("<stages/>", etree.tostring(self.stages.to_xml()))
        self.assertEquals("<stages/>\n", self.stages.to_xml_string())

    def test_nofile(self):
        # function should return false when file doesn't exist
        self.assertFalse(self.stages.read_csv('nofile.csv'))
        self.assertFalse(self.stages.read_csv(''))

        # function should throw an error when no filename is set
        self.assertRaises(TypeError, self.stages.read_csv)

    def test_read_csv(self):
        # read and parse sample file
        self.assertTrue(self.stages.read_csv(TEST_SAMPLE_FILE))

        # test number of stages
        self.assertEquals(3, len(self.stages.stages))

        # test started_at
        self.assertEqual('2014-04-01T18:58:55', self.stages.started_at)

        # test finished_at
        self.assertEqual('2014-04-01T18:59:12', self.stages.finished_at)

        # test stages (names + duration)
        self.assertListEqual(
           [{'duration': 2,
             'finished_at': '2014-04-01T18:58:57',
             'name': 'stage1',
             'started_at': '2014-04-01T18:58:55'},
            {'duration': 5,
             'finished_at': '2014-04-01T18:59:02',
             'name': 'stage2',
             'started_at': '2014-04-01T18:58:57'},
            {'duration': 10,
             'finished_at': '2014-04-01T18:59:12',
             'name': 'stage3',
             'started_at': '2014-04-01T18:59:02'}],
            self.stages.stages)

    def test_parse_timestamps_end(self):
        # use 'end' to end timestamp parsing
        self.stages.parse_timestamps([["stage1","1396378735"],["end","1396378752"], ["end","1396378755"]])

        self.assertListEqual(STAGES_RESULT, self.stages.stages)

    def test_parse_timestamps_caps(self):
        # use 'End' to end timestamp parsing
        self.stages.parse_timestamps([["stage1","1396378735"],["End","1396378752"], ["end","1396378755"]])

        self.assertListEqual(STAGES_RESULT, self.stages.stages)

    def test_parse_timestamps_end_no_match(self):
        # use 'end_tag' as stage name, this shouldn't end time parsing
        self.stages.parse_timestamps([["stage1","1396378735"],["end_tag","1396378752"], ["end","1396378755"]])

        self.assertListEqual(
           [{'duration': 17,
             'finished_at': '2014-04-01T18:59:12',
             'name': 'stage1',
             'started_at': '2014-04-01T18:58:55'},
            {'duration': 3,
             'finished_at': '2014-04-01T18:59:15',
             'name': 'end_tag',
             'started_at': '2014-04-01T18:59:12'}],
            self.stages.stages)

    def test_parse_timestamps_done(self):
        # use 'done' as end stage name
        self.stages.parse_timestamps([["stage1","1396378735"],["done","1396378752"], ["end","1396378755"]])

        self.assertListEqual(STAGES_RESULT, self.stages.stages)

    def test_parse_timestamps_finished(self):
        # use 'done' as end stage name
        self.stages.parse_timestamps([["stage1","1396378735"],["finished","1396378752"], ["end","1396378755"]])

        self.assertListEqual(STAGES_RESULT, self.stages.stages)

    def test_parse_timestamps_completed(self):
        # use 'done' as end stage name
        self.stages.parse_timestamps([["stage1","1396378735"],["completed","1396378752"], ["end","1396378755"]])

        self.assertListEqual(STAGES_RESULT, self.stages.stages)

    def test_total_duration(self):
        # read and parse sample file
        self.assertTrue(self.stages.read_csv(TEST_SAMPLE_FILE))

        # test total duration
        self.assertEqual(17, self.stages.total_duration())

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
