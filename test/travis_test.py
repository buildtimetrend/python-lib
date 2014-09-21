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

from buildtimetrend.travis import *
import constants
import unittest

TEST_REPO = 'ruleant/buildtime-trend'
TEST_BUILD = '158'
VALID_HASH1 = '1234abcd'
VALID_HASH2 = '1234abce'
INVALID_HASH = 'abcd1234'
DURATION_NANO = 11000000000
DURATION_SEC = 11.0

class TestTravisData(unittest.TestCase):
    def setUp(self):
        self.travis_data = TravisData(TEST_REPO, TEST_BUILD)

    def test_novalue(self):
         # data should be empty
        self.assertEquals(0, len(self.travis_data.build_data))
        self.assertEquals(None, self.travis_data.get_started_at())

    def test_gather_data(self):
        # retrieve data from Travis API
        self.travis_data.get_build_data()
        self.assertTrue(len(self.travis_data.build_data) > 0)

        # retrieve start time
        self.assertEquals(
            '2014-07-08T11:18:13Z',
            self.travis_data.get_started_at())


class TestTravisSubstage(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.substage = TravisSubstage()

    def test_novalue(self):
         # data should be empty
        self.assertFalse(self.substage.has_name())
        self.assertFalse(self.substage.has_timing_hash())
        self.assertFalse(self.substage.has_command())
        self.assertFalse(self.substage.has_started())
        self.assertFalse(self.substage.has_finished())
        self.assertFalse(self.substage.finished_incomplete)
        self.assertEquals("", self.substage.get_name())
        self.assertDictEqual(
            {"name": "", "duration": 0},
            self.substage.stage.to_dict())
        self.assertEquals("", self.substage.timing_hash)

    def test_param_is_not_dict(self):
        # error is thrown when called without parameters
        self.assertRaises(TypeError, self.substage.process_parsed_tags)
        self.assertRaises(TypeError, self.substage.process_start_stage)
        self.assertRaises(TypeError, self.substage.process_start_time)
        self.assertRaises(TypeError, self.substage.process_command)
        self.assertRaises(TypeError, self.substage.process_end_time)
        self.assertRaises(TypeError, self.substage.process_end_stage)

        # error is thrown when called with an invalid parameter
        self.assertRaises(TypeError, self.substage.process_parsed_tags, None)
        self.assertRaises(TypeError, self.substage.process_start_stage, None)
        self.assertRaises(TypeError, self.substage.process_start_time, None)
        self.assertRaises(TypeError, self.substage.process_command, None)
        self.assertRaises(TypeError, self.substage.process_end_time, None)
        self.assertRaises(TypeError, self.substage.process_end_stage, None)

        self.assertRaises(TypeError, self.substage.process_parsed_tags, "string")
        self.assertRaises(TypeError, self.substage.process_start_stage, "string")
        self.assertRaises(TypeError, self.substage.process_start_time, "string")
        self.assertRaises(TypeError, self.substage.process_command, "string")
        self.assertRaises(TypeError, self.substage.process_end_time, "string")
        self.assertRaises(TypeError, self.substage.process_end_stage, "string")

    def test_process_parsed_tags_full(self):
        # dict shouldn't be processed if it doesn't contain the required tags
        self.assertFalse(self.substage.process_parsed_tags({'invalid': 'param'}))
        self.assertFalse(self.substage.has_started())
        self.assertFalse(self.substage.has_finished())

        # dict shouldn't be processed if it doesn't contain the required tags
        self.assertFalse(self.substage.process_parsed_tags({'start_stage': 'stage'}))
        self.assertFalse(self.substage.has_started())
        self.assertFalse(self.substage.has_finished())

        # pass a valid start tag
        self.assertTrue(self.substage.process_parsed_tags({
            'start_stage': 'stage1', 'start_substage': 'substage1'
        }))
        self.assertTrue(self.substage.has_started())
        self.assertEquals("stage1.substage1", self.substage.stage.data["name"])
        self.assertFalse(self.substage.has_finished())

        # pass a valid timing hash
        self.assertTrue(self.substage.process_parsed_tags({'start_hash': VALID_HASH1}))
        self.assertTrue(self.substage.has_started())
        self.assertEquals(VALID_HASH1, self.substage.timing_hash)
        self.assertFalse(self.substage.has_finished())

        # pass a valid command name
        self.assertTrue(self.substage.process_parsed_tags({'command': 'command1.sh'}))
        self.assertTrue(self.substage.has_started())
        self.assertEquals('command1.sh', self.substage.stage.data["command"])
        self.assertFalse(self.substage.has_finished())

        # pass valid timing data
        self.assertTrue(self.substage.process_parsed_tags({
            'end_hash': VALID_HASH1,
            'start_timestamp': constants.TIMESTAMP_NANO_STARTED,
            'finish_timestamp': constants.TIMESTAMP_NANO_FINISHED,
            'duration': DURATION_NANO
        }))
        self.assertFalse(self.substage.has_finished())
        self.assertDictEqual(constants.SPLIT_TIMESTAMP_STARTED,
            self.substage.stage.data["started_at"])
        self.assertDictEqual(constants.SPLIT_TIMESTAMP_FINISHED,
            self.substage.stage.data["finished_at"])
        self.assertEquals(DURATION_SEC, self.substage.stage.data["duration"])

        # pass valid end tag
        self.assertTrue(self.substage.process_parsed_tags({
            'end_stage': 'stage1', 'end_substage': 'substage1'
        }))
        self.assertFalse(self.substage.finished_incomplete)
        self.assertTrue(self.substage.has_finished())

        # test stage
        self.assertDictEqual(
            {
                "name": "stage1.substage1",
                "duration": DURATION_SEC,
                "command": "command1.sh",
                "started_at": constants.SPLIT_TIMESTAMP_STARTED,
                "finished_at": constants.SPLIT_TIMESTAMP_FINISHED
            },
            self.substage.stage.to_dict()
        )

    def test_process_parsed_tags_no_starttag(self):
        # pass a valid timing hash
        self.assertTrue(self.substage.process_parsed_tags({'start_hash': VALID_HASH1}))
        self.assertTrue(self.substage.has_started())
        self.assertEquals(VALID_HASH1, self.substage.timing_hash)
        self.assertFalse(self.substage.has_finished())

        # pass a valid command name
        self.assertTrue(self.substage.process_parsed_tags({'command': 'command1.sh'}))
        self.assertTrue(self.substage.has_started())
        self.assertEquals('command1.sh', self.substage.stage.data["command"])
        self.assertFalse(self.substage.has_finished())

        # pass valid timing data
        self.assertTrue(self.substage.process_parsed_tags({
            'end_hash': VALID_HASH1,
            'start_timestamp': constants.TIMESTAMP_NANO_STARTED,
            'finish_timestamp': constants.TIMESTAMP_NANO_FINISHED,
            'duration': DURATION_NANO
        }))
        self.assertTrue(self.substage.has_finished())

        # test stage
        self.assertDictEqual(
            {
                # TODO assign substage name
                "name": "",
                "duration": DURATION_SEC,
                "command": "command1.sh",
                "started_at": constants.SPLIT_TIMESTAMP_STARTED,
                "finished_at": constants.SPLIT_TIMESTAMP_FINISHED
            },
            self.substage.stage.to_dict()
        )

    def test_process_parsed_tags_no_timing(self):
        # pass a valid start tag
        self.assertTrue(self.substage.process_parsed_tags({
            'start_stage': 'stage1', 'start_substage': 'substage1'
        }))
        self.assertTrue(self.substage.has_started())
        self.assertEquals("stage1.substage1", self.substage.stage.data["name"])
        self.assertFalse(self.substage.has_finished())

        # pass a valid command name
        self.assertTrue(self.substage.process_parsed_tags({'command': 'command1.sh'}))
        self.assertTrue(self.substage.has_started())
        self.assertEquals('command1.sh', self.substage.stage.data["command"])
        self.assertFalse(self.substage.has_finished())

        # pass valid end tag
        self.assertTrue(self.substage.process_parsed_tags({
            'end_stage': 'stage1', 'end_substage': 'substage1'
        }))
        self.assertFalse(self.substage.finished_incomplete)
        self.assertTrue(self.substage.has_finished())

        # test stage
        self.assertDictEqual(
            {
                "name": "stage1.substage1",
                "duration": 0.0,
                "command": "command1.sh",
            },
            self.substage.stage.to_dict()
        )

    def test_process_start_stage(self):
        # dict shouldn't be processed if it doesn't contain the required tags
        self.assertFalse(self.substage.process_start_stage({'invalid': 'param'}))
        self.assertFalse(self.substage.process_start_stage({'start_stage': 'stage'}))
        self.assertFalse(self.substage.process_start_stage({'start_substage': 'substage'}))

        # pass a valid start tag
        self.assertTrue(self.substage.process_start_stage({
            'start_stage': 'stage1', 'start_substage': 'substage1'
        }))
        self.assertTrue(self.substage.has_started())
        self.assertEquals("stage1.substage1", self.substage.stage.data["name"])
        self.assertFalse(self.substage.has_finished())

        # passing a valid start tag when it was started already, should fail
        self.assertFalse(self.substage.process_start_stage({
            'start_stage': 'stage1', 'start_substage': 'substage2'
        }))
        self.assertTrue(self.substage.has_started())
        self.assertEquals("stage1.substage1", self.substage.stage.data["name"])
        self.assertFalse(self.substage.has_finished())

    def test_process_start_time(self):
        # dict shouldn't be processed if it doesn't contain the required tags
        self.assertFalse(self.substage.process_start_time({'invalid': 'param'}))

        # pass a valid timing hash
        self.assertTrue(self.substage.process_start_time({'start_hash': VALID_HASH1}))
        self.assertTrue(self.substage.has_started())
        self.assertEquals(VALID_HASH1, self.substage.timing_hash)
        self.assertFalse(self.substage.has_finished())

        # passing a valid start tag when it was started already, should fail
        self.assertFalse(self.substage.process_start_time({'start_hash': VALID_HASH2}))
        self.assertTrue(self.substage.has_started())
        self.assertEquals(VALID_HASH1, self.substage.timing_hash)
        self.assertFalse(self.substage.has_finished())

    def test_process_command(self):
        # dict shouldn't be processed if it doesn't contain the required tags
        self.assertFalse(self.substage.process_command({'invalid': 'param'}))

        # call similar tests with a parameter
        self.__check_process_command('command1.sh')

    def test_process_command_has_name(self):
        # assign substage name
        self.substage.process_start_stage({
            'start_stage': 'stage1', 'start_substage': 'substage1'
        })

        # call similar tests with a parameter
        self.__check_process_command('stage1.substage1')

    def __check_process_command(self, expected_command):
        '''similar test for test_process_command*'''
        # pass a valid command name
        self.assertTrue(self.substage.process_command({'command': 'command1.sh'}))
        self.assertTrue(self.substage.has_started())
        self.assertEquals('command1.sh', self.substage.stage.data["command"])
        self.assertEquals(expected_command, self.substage.get_name())

        # passing a valid command when it was started already, should fail
        self.assertFalse(self.substage.process_command({'command': 'command2.sh'}))
        self.assertTrue(self.substage.has_started())
        self.assertEquals('command1.sh', self.substage.stage.data["command"])
        self.assertEquals(expected_command, self.substage.get_name())

    def test_process_end_time_tags(self):
        # dict shouldn't be processed if it doesn't contain the required tags
        self.assertFalse(self.substage.process_end_time({'invalid': 'param'}))
        self.assertFalse(self.substage.process_end_time({'end_hash': VALID_HASH1}))
        self.assertFalse(self.substage.process_end_time({'start_timestamp': constants.TIMESTAMP_NANO_STARTED}))
        self.assertFalse(self.substage.process_end_time({'finish_timestamp': constants.TIMESTAMP_NANO_FINISHED}))
        self.assertFalse(self.substage.process_end_time({'duration': DURATION_NANO}))

    def test_process_end_time_not_started(self):
        # pass a valid start tag but, timing hasn't started
        self.assertFalse(self.substage.process_end_time({
            'end_hash': VALID_HASH1,
            'start_timestamp': constants.TIMESTAMP_NANO_STARTED,
            'finish_timestamp': constants.TIMESTAMP_NANO_FINISHED,
            'duration': DURATION_SEC
        }))
        self.assertTrue(self.substage.finished_incomplete)
        self.assertTrue(self.substage.has_finished())

    def test_process_end_time_invalid_hash(self):
        # timing has started, but hash doesn't match
        self.substage.process_start_time({'start_hash': VALID_HASH1})

        self.assertFalse(self.substage.process_end_time({
            'end_hash': INVALID_HASH,
            'start_timestamp': constants.TIMESTAMP_NANO_STARTED,
            'finish_timestamp': constants.TIMESTAMP_NANO_FINISHED,
            'duration': DURATION_NANO
        }))
        self.assertTrue(self.substage.finished_incomplete)
        self.assertTrue(self.substage.has_finished())

    def test_process_end_time_valid_hash(self):
        # timing has started, hash matches
        self.substage.process_start_time({'start_hash': VALID_HASH1})

        self.assertTrue(self.substage.process_end_time({
            'end_hash': VALID_HASH1,
            'start_timestamp': constants.TIMESTAMP_NANO_STARTED,
            'finish_timestamp': constants.TIMESTAMP_NANO_FINISHED,
            'duration': DURATION_NANO
        }))
        self.assertFalse(self.substage.finished_incomplete)
        self.assertTrue(self.substage.has_finished())

        self.assertDictEqual(constants.SPLIT_TIMESTAMP_STARTED,
            self.substage.stage.data["started_at"])
        self.assertDictEqual(constants.SPLIT_TIMESTAMP_FINISHED,
            self.substage.stage.data["finished_at"])
        self.assertEquals(DURATION_SEC, self.substage.stage.data["duration"])

    def test_process_end_stage_tags(self):
        # dict shouldn't be processed if it doesn't contain the required tags
        self.assertFalse(self.substage.process_end_stage({'invalid': 'param'}))
        self.assertFalse(self.substage.process_end_stage({'end_stage': 'stage1'}))
        self.assertFalse(self.substage.process_end_stage({'end_substage': 'substage1'}))

    def test_process_end_stage_not_started(self):
        # pass a valid end tag but, stage wasn't started
        self.assertFalse(self.substage.process_end_stage({
            'end_stage': 'stage1', 'end_substage': 'substage1'
        }))
        self.assertTrue(self.substage.finished_incomplete)
        self.assertTrue(self.substage.has_finished())

    def test_process_end_time_invalid_name(self):
        # stage was started, but name doesn't match
        self.substage.process_start_stage({
            'start_stage': 'stage1', 'start_substage': 'substage1'
        })

        self.assertFalse(self.substage.process_end_stage({
            'end_stage': 'stage1', 'end_substage': 'substage2'
        }))
        self.assertTrue(self.substage.finished_incomplete)
        self.assertTrue(self.substage.has_finished())

    def test_process_end_time_valid_name(self):
        # stage was started, name matches
        self.substage.process_start_stage({
            'start_stage': 'stage1', 'start_substage': 'substage1'
        })

        self.assertTrue(self.substage.process_end_stage({
            'end_stage': 'stage1', 'end_substage': 'substage1'
        }))
        self.assertFalse(self.substage.finished_incomplete)
        self.assertTrue(self.substage.has_finished())

    def test_get_name(self):
        ''' get_name() returns the name, or the command if name is not set'''
        # set name
        self.substage.stage.set_name("stage.1")
        self.assertEquals("stage.1", self.substage.get_name())

        # set command, should have no influence, nam is already set
        self.substage.command = "command1.sh"
        self.assertEquals("stage.1", self.substage.get_name())

    def test_get_name_command(self):
        ''' get_name() returns the name, or the command if name is not set'''
        # set command
        self.substage.stage.set_command("command1.sh")
        self.assertEquals("command1.sh", self.substage.get_name())

    def test_has_name(self):
        ''' has_name() should return true if name is set'''
        # set name
        self.substage.stage.set_name("stage.1")
        self.assertTrue(self.substage.has_name())

    def test_has_timing_hash(self):
        ''' has_started() should return true if timing_hash is set'''
        # set substage timing hash
        self.substage.timing_hash = VALID_HASH1
        self.assertTrue(self.substage.has_timing_hash())

    def test_has_command(self):
        ''' has_command() should return true if command is set'''
        # set command
        self.substage.stage.set_command("command1.sh")
        self.assertTrue(self.substage.has_command())

    def test_has_started_name(self):
        ''' has_started() should return true if name is set'''
        # set name
        self.substage.stage.set_name("stage.1")
        self.assertTrue(self.substage.has_started())

    def test_has_started_hash(self):
        ''' has_started() should return true if timing_hash is set'''
        # set substage hash
        self.substage.timing_hash = VALID_HASH1
        self.assertTrue(self.substage.has_started())

    def test_has_started_command(self):
        ''' has_started() should return true if command is set'''
        # set command
        self.substage.stage.set_command("command1.sh")
        self.assertTrue(self.substage.has_started())

    def test_has_started_both(self):
        ''' has_started() should return true if name or hash is set'''
        # set name
        self.substage.name = "stage.1"
        # set timing hash
        self.substage.timing_hash = VALID_HASH1
        self.assertTrue(self.substage.has_started())

    def test_has_finished_stage_name(self):
        ''' has_finished() should return true if stagename was closed'''
        self.substage.process_start_stage({
            'start_stage': 'stage1', 'start_substage': 'substage1'
        })

        self.assertTrue(self.substage.process_end_stage({
            'end_stage': 'stage1', 'end_substage': 'substage1'
        }))
        self.assertTrue(self.substage.has_finished())

    def test_has_finished_timestamp(self):
        ''' has_finished() should return true if finished timestamp is set'''
        self.substage.process_start_time({'start_hash': VALID_HASH1})

        self.assertTrue(self.substage.process_end_time({
            'end_hash': VALID_HASH1,
            'start_timestamp': constants.TIMESTAMP_STARTED,
            'finish_timestamp': constants.TIMESTAMP_FINISHED,
            'duration': DURATION_NANO
        }))
        self.assertTrue(self.substage.has_finished())

    def test_has_finished_stage_name(self):
        ''' has_finished() should return true if command is set'''
        self.substage.process_command({'command': 'command1.sh'})
        self.assertTrue(self.substage.has_finished())

    def test_has_finished_incomplete(self):
        ''' has_finished() should return true if finished_incomplete is set'''
        # set finished_incomplete
        self.substage.finished_incomplete = True
        self.assertTrue(self.substage.has_finished())

    def test_has_finished(self):
        '''
        has_finished() should return true if finished timestamp is set
        or if finished_incomplete is set
        '''
        # set finish_timestamp
        self.substage.stage.set_finished_at = constants.TIMESTAMP_FINISHED
        # set finished_incomplete
        self.substage.finished_incomplete = True
        self.assertTrue(self.substage.has_finished())
