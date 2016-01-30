# vim: set expandtab sw=4 ts=4:
#
# Unit tests for logger related functions
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

import buildtimetrend
from buildtimetrend import set_loglevel
import unittest
import logging


class TestLogger(unittest.TestCase):

    """Unit tests for logger related functions"""

    def test_set_loglevel(self):
        """Test set_loglevel()"""
        logger = logging.getLogger(buildtimetrend.NAME)
        # test default loglevel
        self.assertEqual(logging.WARNING, logger.getEffectiveLevel())

        # test setting loglevel to INFO
        set_loglevel("INFO")
        self.assertEqual(logging.INFO, logger.getEffectiveLevel())

        # test setting loglevel to DEBUG
        set_loglevel("DEBUG")
        self.assertEqual(logging.DEBUG, logger.getEffectiveLevel())

        # test setting loglevel to ERROR
        set_loglevel("ERROR")
        self.assertEqual(logging.ERROR, logger.getEffectiveLevel())

        # test setting loglevel to CRITICAL
        set_loglevel("CRITICAL")
        self.assertEqual(logging.CRITICAL, logger.getEffectiveLevel())

        # test setting loglevel to WARNING
        set_loglevel("WARNING")
        self.assertEqual(logging.WARNING, logger.getEffectiveLevel())

        # error is thrown when called without parameters
        self.assertRaises(TypeError, set_loglevel)

        # error is thrown when called with an invalid parameter
        self.assertRaises(TypeError, set_loglevel, None)
        self.assertRaises(ValueError, set_loglevel, "invalid")

        # passing invalid tags should not change log level
        self.assertEqual(logging.WARNING, logger.getEffectiveLevel())
