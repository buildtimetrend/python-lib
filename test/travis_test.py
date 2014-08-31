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
import unittest

TEST_REPO = 'ruleant/buildtime-trend'
TEST_BUILD = '158'

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
        self.substage = TravisSubstage()

    def test_novalue(self):
         # data should be empty
        self.assertFalse(self.substage.has_started())
        self.assertFalse(self.substage.has_finished())
        self.assertEquals("", self.substage.name)
        self.assertEquals("", self.substage.substage_hash)
        self.assertEquals("", self.substage.command)
        self.assertEquals(0, self.substage.start_timestamp)
        self.assertEquals(0, self.substage.finish_timestamp)
        self.assertEquals(0, self.substage.duration)

    def test_has_started_name(self):
        ''' has_started() should return true if name is set'''
        # set name
        self.substage.name = "stage.1"
        self.assertTrue(self.substage.has_started())

    def test_has_started_hash(self):
        ''' has_started() should return true if substage_hash is set'''
        # set substage hash
        self.substage.substage_hash = "1234abcd"
        self.assertTrue(self.substage.has_started())

    def test_has_started_both(self):
        ''' has_started() should return true if name or hash is set'''
        # set name
        self.substage.name = "stage.1"
        # set substage hash
        self.substage.substage_hash = "1234abcd"
        self.assertTrue(self.substage.has_started())

    def test_has_finished_timestamp(self):
        ''' has_finished() should return true if finished timestamp is set'''
        # set finish_timestamp
        self.substage.finish_timestamp = 12345678
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
        self.substage.finish_timestamp = 12345678
        # set finished_incomplete
        self.substage.finished_incomplete = True
        self.assertTrue(self.substage.has_finished())
