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

from buildtimetrend.trend import Trend
import unittest

TEST_SAMPLE_FILE = 'buildtimetrend/test/testsample_buildtimes.xml'


class TestTrend(unittest.TestCase):
    def setUp(self):
        self.trend = Trend()

    def test_novalue(self):
         # number of builds and stages should be zero
        self.assertEquals(0, len(self.trend.builds))
        self.assertEquals(0, len(self.trend.stages))

    def test_nofile(self):
        # function should return false when file doesn't exist
        self.assertFalse(self.trend.gather_data('nofile.xml'))
        self.assertFalse(self.trend.gather_data(''))

        # function should throw an error when no filename is set
        self.assertRaises(TypeError, self.trend.gather_data)

    def test_gather_data(self):
        # read and parse sample file
        self.assertTrue(self.trend.gather_data(TEST_SAMPLE_FILE))

        # test number of builds and stages
        self.assertEquals(3, len(self.trend.builds))
        self.assertEquals(5, len(self.trend.stages))

        # test buildnames
        self.assertListEqual(['10', '11.1', '#3'], self.trend.builds)

        # test stages (names + duration)
        self.assertDictEqual(
            {'stage1': [4, 3, 2], 'stage2': [5, 6, 7], 'stage3': [10, 11, 12],
            'stage4': [1, 0, 3], 'stage5': [0, 6, 0]},
            self.trend.stages)
