# vim: set expandtab sw=4 ts=4:
#
# Unit tests for Trend class
#
# Copyright (C) 2014-2016 Dieter Adriaenssens <ruleant@users.sourceforge.net>
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

from buildtimetrend.trend import Trend
import os
from buildtimetrend import tools
import unittest

TEST_SAMPLE_FILE = 'buildtimetrend/test/testsample_buildtimes.xml'
TEST_TREND_FILE = '/tmp/test_trend.png'


class TestTrend(unittest.TestCase):

    """Unit tests for Trend class"""

    def setUp(self):
        """Initialise test environment before each test."""
        self.trend = Trend()

    def tearDown(self):
        """Clean up after tests"""
        if (tools.check_file(TEST_TREND_FILE)):
            os.remove(TEST_TREND_FILE)

    def test_novalue(self):
        """Test freshly initialised object."""
        # number of builds and stages should be zero
        self.assertEqual(0, len(self.trend.builds))
        self.assertEqual(0, len(self.trend.stages))

    def test_nofile(self):
        """Test gather_data() with no file."""
        # function should return false when file doesn't exist
        self.assertFalse(self.trend.gather_data('nofile.xml'))
        self.assertFalse(self.trend.gather_data(''))

        # function should throw an error when no filename is set
        self.assertRaises(TypeError, self.trend.gather_data)

    def test_gather_data(self):
        """Test gather_data()"""
        # read and parse sample file
        self.assertTrue(self.trend.gather_data(TEST_SAMPLE_FILE))

        # test number of builds and stages
        self.assertEqual(3, len(self.trend.builds))
        self.assertEqual(5, len(self.trend.stages))

        # test buildnames
        self.assertListEqual(['10', '11.1', '#3'], self.trend.builds)

        # test stages (names + duration)
        self.assertDictEqual(
            {'stage1': [4, 3, 2], 'stage2': [5, 6, 7], 'stage3': [10, 11, 12],
             'stage4': [1, 0, 3], 'stage5': [0, 6, 0]},
            self.trend.stages)

    def test_generate(self):
        """Test generate()"""
        self.trend.builds = ['10', '11.1', '#3']
        self.trend.stages = {
            'stage1': [4, 3, 2],
            'stage2': [5, 6, 7],
            'stage3': [10, 11, 12],
            'stage4': [1, 0, 3],
            'stage5': [0, 6, 0]
        }

        self.assertFalse(tools.check_file(TEST_TREND_FILE))
        self.trend.generate(TEST_TREND_FILE)
        self.assertTrue(tools.check_file(TEST_TREND_FILE))
