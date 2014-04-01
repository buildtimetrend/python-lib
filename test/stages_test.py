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
import unittest

TEST_SAMPLE_FILE = 'test/testsample_timestamps.csv'


class TestTimestamps(unittest.TestCase):
    def setUp(self):
        self.stages = Stages()

    def test_novalue(self):
         # number of stages should be zero
        self.assertEquals(0, len(self.stages.stages))

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
            {'stage1': 2, 'stage2': 5, 'stage3': 10}, self.stages.stages)

if __name__ == '__main__':
    unittest.main()
