# vim: set expandtab sw=4 ts=4:
#
# Unit tests for Stages class
#
# Copyright (C) 2014-2015 Dieter Adriaenssens <ruleant@users.sourceforge.net>
#
# This file is part of buildtimetrend/python-lib
# <https://github.com/buildtimetrend/python-lib/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from buildtimetrend.stages import Stages
from buildtimetrend.stages import Stage
import constants
from lxml import etree
import unittest

STAGES_RESULT = [{
    'duration': 17.0,
    'finished_at': constants.SPLIT_TIMESTAMP4,
    'name': 'stage1',
    'started_at': constants.SPLIT_TIMESTAMP1
}]


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
        self.assertEquals(b"<stages/>", etree.tostring(self.stages.to_xml()))
        self.assertEquals(b"<stages/>\n", self.stages.to_xml_string())

    def test_nofile(self):
        # function should return false when file doesn't exist
        self.assertFalse(self.stages.read_csv('nofile.csv'))
        self.assertFalse(self.stages.read_csv(''))

        # function should throw an error when no filename is set
        self.assertRaises(TypeError, self.stages.read_csv)

    def test_set_end_timestamp(self):
        self.assertEquals(0, self.stages.end_timestamp)

        self.stages.set_end_timestamp("string")
        self.assertEquals(0, self.stages.end_timestamp)

        self.stages.set_end_timestamp(23.45)
        self.assertEquals(23.45, self.stages.end_timestamp)

        self.stages.set_end_timestamp(123)
        self.assertEquals(123, self.stages.end_timestamp)

    def test_read_csv(self):
        # read and parse sample file
        self.assertTrue(
            self.stages.read_csv(constants.TEST_SAMPLE_TIMESTAMP_FILE)
        )

        # test number of stages
        self.assertEquals(3, len(self.stages.stages))

        # test started_at
        self.assertEqual(constants.SPLIT_TIMESTAMP1, self.stages.started_at)

        # test finished_at
        self.assertEqual(constants.SPLIT_TIMESTAMP4, self.stages.finished_at)

        # test stages (names + duration)
        self.assertListEqual(
            [
                {
                    'duration': 2,
                    'finished_at': constants.SPLIT_TIMESTAMP2,
                    'name': 'stage1',
                    'started_at': constants.SPLIT_TIMESTAMP1
                },
                {
                    'duration': 5,
                    'finished_at': constants.SPLIT_TIMESTAMP3,
                    'name': 'stage2',
                    'started_at': constants.SPLIT_TIMESTAMP2
                },
                {
                    'duration': 10,
                    'finished_at': constants.SPLIT_TIMESTAMP4,
                    'name': 'stage3',
                    'started_at': constants.SPLIT_TIMESTAMP3
                }
            ],
            self.stages.stages)

    def test_parse_timestamps_end(self):
        # use 'end' to end timestamp parsing
        self.stages.parse_timestamps([
            ["stage1", constants.TIMESTAMP1],
            ["end", constants.TIMESTAMP4],
            ["end", "1396378755"]])

        self.assertListEqual(STAGES_RESULT, self.stages.stages)

    def test_parse_timestamps_caps(self):
        # use 'End' to end timestamp parsing
        self.stages.parse_timestamps([
            ["stage1", constants.TIMESTAMP1],
            ["End", constants.TIMESTAMP4],
            ["end", "1396378755"]])

        self.assertListEqual(STAGES_RESULT, self.stages.stages)

    def test_parse_timestamps_end_no_match(self):
        # use 'end_tag' as stage name, this shouldn't end time parsing
        self.stages.parse_timestamps([
            ["stage1", constants.TIMESTAMP1],
            ["end_tag", constants.TIMESTAMP4],
            ["end", "1396378755"]])

        self.assertListEqual(
            [
                {
                    'duration': 17,
                    'finished_at': constants.SPLIT_TIMESTAMP4,
                    'name': 'stage1',
                    'started_at': constants.SPLIT_TIMESTAMP1
                },
                {
                    'duration': 3,
                    'finished_at': constants.SPLIT_TIMESTAMP_ENDTAG,
                    'name': 'end_tag',
                    'started_at': constants.SPLIT_TIMESTAMP4
                }
            ],
            self.stages.stages)

    def test_parse_timestamps_done(self):
        # use 'done' as end stage name
        self.stages.parse_timestamps([
            ["stage1", constants.TIMESTAMP1],
            ["done", constants.TIMESTAMP4],
            ["end", "1396378755"]])

        self.assertListEqual(STAGES_RESULT, self.stages.stages)

    def test_parse_timestamps_finished(self):
        # use 'end' as end stage name
        self.stages.parse_timestamps([
            ["stage1", constants.TIMESTAMP1],
            ["finished", constants.TIMESTAMP4],
            ["end", "1396378755"]])

        self.assertListEqual(STAGES_RESULT, self.stages.stages)

    def test_parse_timestamps_completed(self):
        # use 'completed' as end stage name
        self.stages.parse_timestamps([
            ["stage1", constants.TIMESTAMP1],
            ["completed", constants.TIMESTAMP4],
            ["end", "1396378755"]])

        self.assertListEqual(STAGES_RESULT, self.stages.stages)

    def test_parse_timestamps_end_timestamp(self):
        # no end_timestamp set
        self.stages.parse_timestamps([["stage1", constants.TIMESTAMP1]])
        self.assertEqual(0, len(self.stages.stages))

        # with end_timestamp set
        self.stages.set_end_timestamp(constants.TIMESTAMP4)
        self.stages.parse_timestamps([["stage1", constants.TIMESTAMP1]])
        self.assertEqual(1, len(self.stages.stages))
        self.assertListEqual(STAGES_RESULT, self.stages.stages)

    def test_parse_timestamps_nanoseconds(self):
        self.stages.set_end_timestamp(constants.TIMESTAMP_FINISHED)

        self.stages.parse_timestamps([["stage1", constants.TIMESTAMP_STARTED]])

        self.assertListEqual(
            [
                {
                    'duration': constants.STAGE_DURATION,
                    'finished_at': constants.SPLIT_TIMESTAMP_FINISHED,
                    'name': 'stage1',
                    'started_at': constants.SPLIT_TIMESTAMP_STARTED
                }
            ],
            self.stages.stages)

        # test total duration
        self.assertEqual(constants.STAGE_DURATION, self.stages.total_duration())

    def test_create_stage(self):
        self.assertEqual(
            None,
            self.stages.create_stage("stage1", "string", "string")
        )
        self.assertEqual(None, self.stages.create_stage("stage1", 1, "string"))
        self.assertEqual(None, self.stages.create_stage("stage1", "string", 1))
        self.assertTrue(isinstance(self.stages.create_stage("stage1", 1, 2), Stage))
        self.assertTrue(
            isinstance(self.stages.create_stage("stage1", 1.0, 2.0), Stage)
        )

        self.assertDictEqual(
            {'duration': 17,
             'finished_at': constants.SPLIT_TIMESTAMP4,
             'name': 'stage1',
             'started_at': constants.SPLIT_TIMESTAMP1},
            self.stages.create_stage(
                "stage1",
                constants.TIMESTAMP1,
                constants.TIMESTAMP4
            ).to_dict()
        )

        self.assertDictEqual(
            {'duration': constants.STAGE_DURATION,
             'finished_at': constants.SPLIT_TIMESTAMP_FINISHED,
             'name': 'stage1',
             'started_at': constants.SPLIT_TIMESTAMP_STARTED},
            self.stages.create_stage(
                "stage1",
                constants.TIMESTAMP_STARTED,
                constants.TIMESTAMP_FINISHED
            ).to_dict()
        )

    def test_total_duration(self):
        # read and parse sample file
        self.assertTrue(
            self.stages.read_csv(constants.TEST_SAMPLE_TIMESTAMP_FILE)
        )

        # test total duration
        self.assertEqual(17, self.stages.total_duration())

    def test_to_xml(self):
        # read and parse sample file
        self.stages.read_csv(constants.TEST_SAMPLE_TIMESTAMP_FILE)

        # test xml output
        self.assertEquals(
            b'<stages><stage duration="2.0" name="stage1"/>'
            b'<stage duration="5.0" name="stage2"/>'
            b'<stage duration="10.0" name="stage3"/></stages>',
            etree.tostring(self.stages.to_xml()))

    def test_to_xml_string(self):
        # read and parse sample file
        self.stages.read_csv(constants.TEST_SAMPLE_TIMESTAMP_FILE)

        # test xml string output
        self.assertEquals(
            b'<stages>\n'
            b'  <stage duration="2.0" name="stage1"/>\n'
            b'  <stage duration="5.0" name="stage2"/>\n'
            b'  <stage duration="10.0" name="stage3"/>\n'
            b'</stages>\n',
            self.stages.to_xml_string())

    def test_add_stage(self):
        # error is thrown when called without parameters
        self.assertRaises(TypeError, self.stages.add_stage)

        # error is thrown when called with an invalid parameter
        self.assertRaises(TypeError, self.stages.add_stage, None)
        self.assertRaises(TypeError, self.stages.add_stage, "string")

        # add a stage
        stage = Stage()
        stage.set_name("stage1")
        stage.set_started_at(constants.TIMESTAMP_STARTED)
        stage.set_finished_at(constants.TIMESTAMP1)
        stage.set_duration(235)

        self.stages.add_stage(stage)

        # test number of stages
        self.assertEquals(1, len(self.stages.stages))

        # test started_at
        self.assertEqual(
            constants.SPLIT_TIMESTAMP_STARTED,
            self.stages.started_at
        )

        # test finished_at
        self.assertEqual(constants.SPLIT_TIMESTAMP1, self.stages.finished_at)

        # test stages (names + duration)
        self.assertListEqual(
            [
                {
                    'duration': 235,
                    'finished_at': constants.SPLIT_TIMESTAMP1,
                    'name': 'stage1',
                    'started_at': constants.SPLIT_TIMESTAMP_STARTED
                }
            ],
            self.stages.stages)

        # add another stage
        stage = Stage()
        stage.set_name("stage2")
        stage.set_started_at(constants.TIMESTAMP1)
        stage.set_finished_at(constants.TIMESTAMP_FINISHED)
        stage.set_duration(136.234)

        self.stages.add_stage(stage)

        # test number of stages
        self.assertEquals(2, len(self.stages.stages))

        # test started_at
        self.assertEqual(
            constants.SPLIT_TIMESTAMP_STARTED,
            self.stages.started_at
        )

        # test finished_at
        self.assertEqual(
            constants.SPLIT_TIMESTAMP_FINISHED,
            self.stages.finished_at
        )

        # test stages (names + duration)
        self.assertListEqual(
            [
                {
                    'duration': 235,
                    'finished_at': constants.SPLIT_TIMESTAMP1,
                    'name': 'stage1',
                    'started_at': constants.SPLIT_TIMESTAMP_STARTED
                },
                {
                    'duration': 136.234,
                    'finished_at': constants.SPLIT_TIMESTAMP_FINISHED,
                    'name': 'stage2',
                    'started_at': constants.SPLIT_TIMESTAMP1
                }
            ],
            self.stages.stages)

    def test_add_stage_incomplete(self):
        # add a stage without started_at timestamp
        stage = Stage()
        stage.set_name("stage1")
        stage.set_finished_at(constants.TIMESTAMP1)
        stage.set_duration(235)

        self.stages.add_stage(stage)

        # test number of stages
        self.assertEquals(1, len(self.stages.stages))

        # test started_at
        self.assertEqual(None, self.stages.started_at)

        # test finished_at
        self.assertEqual(constants.SPLIT_TIMESTAMP1, self.stages.finished_at)

        # test stages (names + duration)
        self.assertListEqual(
            [
                {
                    'duration': 235,
                    'finished_at': constants.SPLIT_TIMESTAMP1,
                    'name': 'stage1'
                }
            ],
            self.stages.stages)

        # add another stage without finished_at timestamp
        stage = Stage()
        stage.set_name("stage2")
        stage.set_started_at(constants.TIMESTAMP1)
        stage.set_duration(136.234)

        self.stages.add_stage(stage)

        # test number of stages
        self.assertEquals(2, len(self.stages.stages))

        # test started_at
        self.assertEqual(constants.SPLIT_TIMESTAMP1, self.stages.started_at)

        # test finished_at
        self.assertEqual(constants.SPLIT_TIMESTAMP1, self.stages.finished_at)

        # test stages (names + duration)
        self.assertListEqual(
            [
                {
                    'duration': 235,
                    'finished_at': constants.SPLIT_TIMESTAMP1,
                    'name': 'stage1'
                },
                {
                    'duration': 136.234,
                    'name': 'stage2',
                    'started_at': constants.SPLIT_TIMESTAMP1
                }
            ],
            self.stages.stages)


class TestStage(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.stage = Stage()

    def test_novalue(self):
        # number of stages should be zero
        self.assertEquals(2, len(self.stage.data))
        # test total duration
        self.assertDictEqual({"name": "", "duration": 0}, self.stage.to_dict())

    def test_set_name(self):
        # name should be a string
        self.assertFalse(self.stage.set_name(None))
        self.assertDictEqual({"name": "", "duration": 0}, self.stage.to_dict())

        # set name
        self.assertTrue(self.stage.set_name("stage_name"))
        self.assertDictEqual(
            {"name": "stage_name", "duration": 0},
            self.stage.to_dict())

        # name can be an empty string
        self.assertTrue(self.stage.set_name(""))
        self.assertDictEqual({"name": "", "duration": 0}, self.stage.to_dict())

    def test_set_command(self):
        # command should be a string
        self.assertFalse(self.stage.set_command(None))
        self.assertDictEqual({"name": "", "duration": 0}, self.stage.to_dict())

        # set command
        self.assertTrue(self.stage.set_command("command1.sh"))
        self.assertDictEqual(
            {"name": "", "duration": 0, "command": "command1.sh"},
            self.stage.to_dict())

        # command can be an empty string
        self.assertTrue(self.stage.set_command(""))
        self.assertDictEqual(
            {"name": "", "duration": 0, "command": ""},
            self.stage.to_dict())

    def test_set_duration(self):
        # duration should be a number
        self.assertFalse(self.stage.set_duration(None))
        self.assertDictEqual({"name": "", "duration": 0}, self.stage.to_dict())
        self.assertFalse(self.stage.set_duration("text"))
        self.assertDictEqual({"name": "", "duration": 0}, self.stage.to_dict())

        # duration can't be a negative value
        self.assertFalse(self.stage.set_duration(-1))
        self.assertDictEqual({"name": "", "duration": 0}, self.stage.to_dict())

        # set duration
        self.assertTrue(self.stage.set_duration(123))
        self.assertDictEqual(
            {"name": "", "duration": 123},
            self.stage.to_dict()
        )
        self.assertTrue(self.stage.set_duration(123.456))
        self.assertDictEqual(
            {"name": "", "duration": 123.456},
            self.stage.to_dict())

        # duration can be zero
        self.assertTrue(self.stage.set_duration(0))
        self.assertDictEqual({"name": "", "duration": 0}, self.stage.to_dict())

    def test_set_duration_nano(self):
        # duration should be a number
        self.assertFalse(self.stage.set_duration_nano(None))
        self.assertDictEqual({"name": "", "duration": 0}, self.stage.to_dict())
        self.assertFalse(self.stage.set_duration_nano("text"))
        self.assertDictEqual({"name": "", "duration": 0}, self.stage.to_dict())

        # duration can't be a negative value
        self.assertFalse(self.stage.set_duration_nano(-1))
        self.assertDictEqual({"name": "", "duration": 0}, self.stage.to_dict())

        # set duration
        self.assertTrue(self.stage.set_duration_nano(123456789))
        self.assertDictEqual(
            {"name": "", "duration": 0.123456789},
            self.stage.to_dict()
        )
        self.assertTrue(self.stage.set_duration_nano(123456789.123))
        self.assertDictEqual(
            {"name": "", "duration": 0.123456789123},
            self.stage.to_dict())

        # duration can be zero
        self.assertTrue(self.stage.set_duration_nano(0))
        self.assertDictEqual({"name": "", "duration": 0}, self.stage.to_dict())

    def test_set_timestamp(self):
        # timestamp should be valid
        self.assertFalse(self.stage.set_timestamp("event1", None))
        self.assertDictEqual({"name": "", "duration": 0}, self.stage.to_dict())
        self.assertFalse(self.stage.set_timestamp("event1", "text"))
        self.assertDictEqual({"name": "", "duration": 0}, self.stage.to_dict())

        # test 0 timestamp (epoch)
        self.assertTrue(self.stage.set_timestamp("event1", 0))
        self.assertDictEqual(
            constants.SPLIT_TIMESTAMP_EPOCH,
            self.stage.data["event1"]
        )
        self.assertDictEqual(
            {
                "name": "",
                "duration": 0,
                "event1": constants.SPLIT_TIMESTAMP_EPOCH},
            self.stage.to_dict())

        # test timestamp
        self.assertTrue(
            self.stage.set_timestamp("event1", constants.TIMESTAMP_TESTDATE)
        )
        self.assertDictEqual(
            constants.SPLIT_TIMESTAMP_TESTDATE,
            self.stage.data["event1"]
        )
        self.assertDictEqual(
            {
                "name": "",
                "duration": 0,
                "event1": constants.SPLIT_TIMESTAMP_TESTDATE},
            self.stage.to_dict())

    def test_set_timestamp_nano(self):
        # test 0 timestamp (epoch)
        self.assertTrue(self.stage.set_timestamp_nano("event1", 0))
        self.assertDictEqual(
            constants.SPLIT_TIMESTAMP_EPOCH,
            self.stage.data["event1"]
        )
        self.assertDictEqual(
            {
                "name": "",
                "duration": 0,
                "event1": constants.SPLIT_TIMESTAMP_EPOCH},
            self.stage.to_dict())

        # test timestamp
        self.assertTrue(
            self.stage.set_timestamp_nano(
                "event1",
                constants.TIMESTAMP_NANO_TESTDATE
            )
        )
        self.assertDictEqual(
            constants.SPLIT_TIMESTAMP_TESTDATE,
            self.stage.data["event1"]
        )
        self.assertDictEqual(
            {
                "name": "",
                "duration": 0,
                "event1": constants.SPLIT_TIMESTAMP_TESTDATE},
            self.stage.to_dict())

    def test_set_started_at(self):
        # timestamp should be valid
        self.assertFalse(self.stage.set_started_at(None))
        self.assertDictEqual({"name": "", "duration": 0}, self.stage.to_dict())
        self.assertFalse(self.stage.set_started_at("text"))
        self.assertDictEqual({"name": "", "duration": 0}, self.stage.to_dict())

        # test 0 timestamp (epoch)
        self.assertTrue(self.stage.set_started_at(0))
        self.assertDictEqual(
            constants.SPLIT_TIMESTAMP_EPOCH,
            self.stage.data["started_at"]
        )
        self.assertDictEqual(
            {
                "name": "",
                "duration": 0,
                "started_at": constants.SPLIT_TIMESTAMP_EPOCH},
            self.stage.to_dict())

        # test timestamp
        self.assertTrue(
            self.stage.set_started_at(constants.TIMESTAMP_TESTDATE)
        )
        self.assertDictEqual(
            constants.SPLIT_TIMESTAMP_TESTDATE,
            self.stage.data["started_at"]
        )
        self.assertDictEqual(
            {
                "name": "",
                "duration": 0,
                "started_at": constants.SPLIT_TIMESTAMP_TESTDATE},
            self.stage.to_dict())

    def test_set_started_at_nano(self):
        # test timestamp
        self.assertTrue(
            self.stage.set_started_at_nano(constants.TIMESTAMP_NANO_TESTDATE)
        )
        self.assertDictEqual(
            constants.SPLIT_TIMESTAMP_TESTDATE,
            self.stage.data["started_at"]
        )
        self.assertDictEqual(
            {
                "name": "",
                "duration": 0,
                "started_at": constants.SPLIT_TIMESTAMP_TESTDATE},
            self.stage.to_dict())

    def test_set_finished_at(self):
        # timestamp should be valid
        self.assertFalse(self.stage.set_finished_at(None))
        self.assertDictEqual({"name": "", "duration": 0}, self.stage.to_dict())
        self.assertFalse(self.stage.set_finished_at("text"))
        self.assertDictEqual({"name": "", "duration": 0}, self.stage.to_dict())

        # test 0 timestamp (epoch)
        self.assertTrue(self.stage.set_finished_at(0))
        self.assertDictEqual(
            constants.SPLIT_TIMESTAMP_EPOCH,
            self.stage.data["finished_at"]
        )
        self.assertDictEqual(
            {
                "name": "",
                "duration": 0,
                "finished_at": constants.SPLIT_TIMESTAMP_EPOCH},
            self.stage.to_dict())

        # test timestamp
        self.assertTrue(
            self.stage.set_finished_at(constants.TIMESTAMP_TESTDATE)
        )
        self.assertDictEqual(
            constants.SPLIT_TIMESTAMP_TESTDATE,
            self.stage.data["finished_at"]
        )
        self.assertDictEqual(
            {
                "name": "",
                "duration": 0,
                "finished_at": constants.SPLIT_TIMESTAMP_TESTDATE},
            self.stage.to_dict())

    def test_set_finished_at_nano(self):
        # test timestamp
        self.assertTrue(
            self.stage.set_finished_at_nano(constants.TIMESTAMP_NANO_TESTDATE)
        )
        self.assertDictEqual(
            constants.SPLIT_TIMESTAMP_TESTDATE,
            self.stage.data["finished_at"]
        )
        self.assertDictEqual(
            {
                "name": "",
                "duration": 0,
                "finished_at": constants.SPLIT_TIMESTAMP_TESTDATE},
            self.stage.to_dict())

    def test_todict(self):
        self.assertTrue(self.stage.set_name("stage.1"))
        self.assertTrue(self.stage.set_duration(11.2345))
        self.assertTrue(self.stage.set_command("command1.sh"))
        self.assertTrue(self.stage.set_started_at(constants.TIMESTAMP_STARTED))
        self.assertTrue(
            self.stage.set_finished_at(constants.TIMESTAMP_FINISHED)
        )
        # test dictionary
        self.assertDictEqual(
            {
                "name": "stage.1",
                "duration": 11.2345,
                "command": "command1.sh",
                "started_at": constants.SPLIT_TIMESTAMP_STARTED,
                "finished_at": constants.SPLIT_TIMESTAMP_FINISHED
            },
            self.stage.to_dict()
        )
