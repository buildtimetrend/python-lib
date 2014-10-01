# vim: set expandtab sw=4 ts=4:
#
# Unit tests for __init__.py
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

from buildtimetrend import *
import logging
import unittest

class TestBuildtimetrend(unittest.TestCase):
    def setUp(self):
        pass

    def test_set_loglevel(self):
        # TODO tests fail, getEffectiveLevel returns 0
        logger = logging.getLogger()
        # test default loglevel
        # self.assertEquals(logging.WARNING, logger.getEffectiveLevel())

        # test setting loglevel to INFO
        set_loglevel("INFO")
        self.assertEquals(logging.INFO, logger.getEffectiveLevel())

        # test setting loglevel to DEBUG
        set_loglevel("DEBUG")
        self.assertEquals(logging.DEBUG, logger.getEffectiveLevel())

        # test setting loglevel to ERROR
        set_loglevel("ERROR")
        self.assertEquals(logging.ERROR, logger.getEffectiveLevel())

        # test setting loglevel to CRITICAL
        set_loglevel("CRITICAL")
        self.assertEquals(logging.CRITICAL, logger.getEffectiveLevel())

        # test setting loglevel to WARNING
        set_loglevel("WARNING")
        self.assertEquals(logging.WARNING, logger.getEffectiveLevel())
