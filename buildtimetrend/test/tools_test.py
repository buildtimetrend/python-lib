# vim: set expandtab sw=4 ts=4:
#
# Unit tests for Tools
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

import buildtimetrend
from buildtimetrend.tools import *
from buildtimetrend.settings import Settings
import os
import unittest
import constants
import logging


class TestTools(unittest.TestCase):
    def setUp(self):
        self.project_info = Settings().get_project_info()
        self.maxDiff = None

    def test_format_timestamp(self):
        # test 0 timestamp (epoch)
        self.assertEquals("1970-01-01T00:00:00", format_timestamp(0))

        # test timestamp
        self.assertEquals("2014-07-09T12:38:33", format_timestamp(1404909513))

    def test_split_timestamp(self):
        # test 0 timestamp (epoch)
        self.assertDictEqual(
            constants.SPLIT_TIMESTAMP_EPOCH, split_timestamp(0)
        )

        # test timestamp
        self.assertDictEqual(
            constants.SPLIT_TIMESTAMP_TESTDATE,
            split_timestamp(constants.TIMESTAMP_TESTDATE)
        )

    def test_split_isotimestamp(self):
        # test 0 timestamp (epoch) in UTC
        self.assertDictEqual(
            constants.SPLIT_TIMESTAMP_EPOCH,
            split_isotimestamp("1970-01-01T00:00:00Z")
        )

        # test 0 timestamp (epoch), without timezone
        self.assertDictEqual(
            constants.SPLIT_TIMESTAMP_EPOCH_NOTZ,
            split_isotimestamp("1970-01-01T00:00:00")
        )

        # test timestamp
        self.assertDictEqual(
            constants.SPLIT_TIMESTAMP_TESTDATE,
            split_isotimestamp(constants.ISOTIMESTAMP_TESTDATE)
        )

    def test_split_datetime(self):
        # error is thrown when called without parameters
        self.assertRaises(TypeError, split_datetime)

        # error is thrown when called with an invalid parameter
        self.assertRaises(TypeError, split_datetime, None)
        self.assertRaises(TypeError, split_datetime, "string")

        # test 0 timestamp (epoch) in UTC
        epoch_utc_dt = datetime.utcfromtimestamp(0).replace(tzinfo=tzutc())
        self.assertDictEqual(
            constants.SPLIT_TIMESTAMP_EPOCH,
            split_datetime(epoch_utc_dt)
        )

        # test 0 timestamp (epoch), without timezone
        epoch_dt = datetime.utcfromtimestamp(0)
        self.assertDictEqual(
            constants.SPLIT_TIMESTAMP_EPOCH_NOTZ,
            split_datetime(epoch_dt)
        )

        # test timestamp
        timestamp_dt = datetime.utcfromtimestamp(constants.TIMESTAMP_TESTDATE).replace(tzinfo=tzutc())
        self.assertDictEqual(
            constants.SPLIT_TIMESTAMP_TESTDATE,
            split_datetime(timestamp_dt)
        )

    def test_nano2sec(self):
        # error is thrown when called without parameters
        self.assertRaises(TypeError, nano2sec)

        # error is thrown when called with an invalid parameter
        self.assertRaises(TypeError, nano2sec, None)
        self.assertRaises(ValueError, nano2sec, "string")

        # test valid parameters
        self.assertEqual(0.0, nano2sec(0))
        self.assertEqual(123.456789123, nano2sec(123456789123))
        self.assertEqual(.123456789123, nano2sec(123456789.123))
        self.assertEqual(-123.456789123, nano2sec(-123456789123))
        self.assertEqual(123.456789123, nano2sec("123456789123"))

    def test_check_file(self):
        # function should return false when file doesn't exist
        self.assertFalse(check_file('nofile.csv'))
        self.assertFalse(check_file(''))

        # function should throw an error when no filename is set
        self.assertRaises(TypeError, check_file)

        # function should return true if file exists
        self.assertTrue(check_file(constants.TEST_SAMPLE_TIMESTAMP_FILE))

    def test_check_dict(self):
        # error is thrown when called without parameters
        self.assertRaises(TypeError, check_dict)

        # error is thrown when called with an invalid parameter
        with self.assertRaises(TypeError) as cm:
            check_dict(None, "name")
        self.assertEqual(
            "param name should be a dictionary", str(cm.exception)
        )

        with self.assertRaises(TypeError) as cm:
            check_dict("string", "string_name")
        self.assertEqual(
            "param string_name should be a dictionary", str(cm.exception)
        )

        # should return true if parameter is a dictionary
        self.assertTrue(check_dict({"string": "test"}, "name"))

        # should return true if key is found in dictionary
        self.assertTrue(check_dict({"string": "test"}, "string"))
        self.assertTrue(check_dict(
            {"string": "test", 7: "test"},
            list({7, "string"})
        ))

        # should return false if key is not found in dictionary
        self.assertTrue(check_dict({"string": "test"}, "name"))

    def test_keys_in_dict(self):
        # empty dict and empty key_list should return true
        self.assertTrue(keys_in_dict({}, []))
        self.assertTrue(keys_in_dict({"string": "test"}, []))

        # find 1 key in dict
        self.assertTrue(keys_in_dict({"string": "test"}, "string"))
        self.assertTrue(keys_in_dict({"string": "test", 7: "test"}, "string"))
        self.assertTrue(keys_in_dict({7: "test"}, 7))
        self.assertTrue(keys_in_dict({"string": "test", 7: "test"}, 7))

        # find multiple keys in dict
        self.assertTrue(keys_in_dict(
            {"string": "test", 7: "test"},
            list({7, "string"})
        ))

        # missing keys
        self.assertFalse(keys_in_dict({"string": "test"}, 7))
        self.assertFalse(keys_in_dict({7: "test"}, "string"))
        self.assertFalse(keys_in_dict({"string": "test"}, list({7, "string"})))

    def test_check_list(self):
        # error is thrown when called without parameters
        self.assertRaises(TypeError, check_list)

        # error is thrown when called with an invalid parameter
        with self.assertRaises(TypeError) as cm:
            check_list(None, "name")
        self.assertEqual("param name should be a list", str(cm.exception))

        with self.assertRaises(TypeError) as cm:
            check_list("string", "string_name")
        self.assertEqual(
            "param string_name should be a list", str(cm.exception)
        )

        # should return true if parameter is a list
        self.assertTrue(check_list(["string", "test"], "name"))

    def test_num_string(self):
        self.assertRaises(TypeError, check_num_string)
        self.assertRaises(TypeError, check_num_string, None)
        self.assertRaises(TypeError, check_num_string, 2.2, "name")
        self.assertRaises(ValueError, check_num_string, "2.2", "name")

        # error is thrown when called with an invalid parameter
        with self.assertRaises(TypeError) as cm:
            check_num_string(None, "name")
        self.assertEqual(
            "param name should be a numerical string or an integer",
            str(cm.exception)
        )

        self.assertEquals(0, check_num_string(0, "name"))
        self.assertEquals(1, check_num_string(1, "name"))
        self.assertEquals(-1, check_num_string(-1, "name"))
        self.assertEquals(2, check_num_string(2, "name"))

        self.assertEquals(0, check_num_string("0", "name"))
        self.assertEquals(1, check_num_string("1", "name"))
        self.assertEquals(-1, check_num_string("-1", "name"))
        self.assertEquals(2, check_num_string("2", "name"))

    def test_set_loglevel(self):
        logger = logging.getLogger(buildtimetrend.NAME)
        # test default loglevel
        self.assertEquals(logging.WARNING, logger.getEffectiveLevel())

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

        # error is thrown when called without parameters
        self.assertRaises(TypeError, set_loglevel)

        # error is thrown when called with an invalid parameter
        self.assertRaises(TypeError, set_loglevel, None)
        self.assertRaises(ValueError, set_loglevel, "invalid")

        # passing invalid tags should not change log level
        self.assertEquals(logging.WARNING, logger.getEffectiveLevel())

    def test_get_repo_slug(self):
        self.assertEquals(None, get_repo_slug())
        self.assertEquals(None, get_repo_slug("abcd", None))
        self.assertEquals(None, get_repo_slug(None, "efgh"))
        self.assertEquals(None, get_repo_slug(None, None))

        self.assertEquals("abcd/efgh", get_repo_slug("abcd", "efgh"))
        self.assertEquals("abcd/efgh", get_repo_slug("Abcd", "eFgh"))
        self.assertEquals("123/456", get_repo_slug(123, 456))
