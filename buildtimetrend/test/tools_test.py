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

from builtins import str
import buildtimetrend
from buildtimetrend.tools import format_timestamp
from buildtimetrend.tools import split_timestamp
from buildtimetrend.tools import split_isotimestamp
from buildtimetrend.tools import split_datetime
from buildtimetrend.tools import nano2sec
from buildtimetrend.tools import check_file
from buildtimetrend.tools import file_is_newer
from buildtimetrend.tools import check_dict
from buildtimetrend.tools import is_dict
from buildtimetrend.tools import keys_in_dict
from buildtimetrend.tools import is_list
from buildtimetrend.tools import is_string
from buildtimetrend.tools import check_num_string
from buildtimetrend.tools import get_repo_slug
from buildtimetrend.settings import Settings
from datetime import datetime
from decimal import Decimal
from dateutil.tz import tzutc
import os
import unittest
import constants


class TestTools(unittest.TestCase):

    """Unit tests for tools functions"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixture."""
        cls.project_info = Settings().get_project_info()
        cls.maxDiff = None

    def test_format_timestamp(self):
        """Test format_timestamp()"""
        # test 0 timestamp (epoch)
        self.assertEqual("1970-01-01T00:00:00", format_timestamp(0))

        # test timestamp
        self.assertEqual("2014-07-09T12:38:33", format_timestamp(1404909513))

    def test_split_timestamp(self):
        """Test split_timestamp()"""
        # error is thrown when called without parameters
        self.assertRaises(TypeError, split_timestamp)

        # error is thrown when called with an invalid parameter
        self.assertRaises(TypeError, split_timestamp, None)
        self.assertRaises(TypeError, split_timestamp, "string")

        # test 0 timestamp (epoch)
        self.assertDictEqual(
            constants.SPLIT_TIMESTAMP_EPOCH, split_timestamp(0)
        )

        # test timestamp
        self.assertDictEqual(
            constants.SPLIT_TIMESTAMP_TESTDATE,
            split_timestamp(nano2sec(constants.TIMESTAMP_NANO_TESTDATE))
        )

        # test timestamp
        self.assertDictEqual(
            constants.SPLIT_TIMESTAMP_STARTED,
            split_timestamp(constants.TIMESTAMP_STARTED)
        )

        # test timestamp
        self.assertDictEqual(
            constants.SPLIT_TIMESTAMP_FINISHED,
            split_timestamp(nano2sec(constants.TIMESTAMP_NANO_FINISHED))
        )

    def test_split_isotimestamp(self):
        """Test split_isotimestamp()"""
        # error is thrown when called without parameters
        self.assertRaises(TypeError, split_isotimestamp)

        # error is thrown when called with an invalid parameter
        self.assertRaises(TypeError, split_isotimestamp, None)
        self.assertRaises(TypeError, split_isotimestamp, 1234)
        self.assertRaises(ValueError, split_isotimestamp, "string")

        # test 0 timestamp (epoch) in UTC
        self.assertDictEqual(
            constants.SPLIT_TIMESTAMP_EPOCH,
            split_isotimestamp("1970-01-01T00:00:00Z")
        )

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
        """Test split_datetime()"""
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
        timestamp_dt = datetime.utcfromtimestamp(constants.TIMESTAMP_TESTDATE)
        timestamp_dt = timestamp_dt.replace(tzinfo=tzutc())

        self.assertDictEqual(
            constants.SPLIT_TIMESTAMP_TESTDATE,
            split_datetime(timestamp_dt)
        )

    def test_nano2sec(self):
        """Test nano2sec()"""
        # error is thrown when called without parameters
        self.assertRaises(TypeError, nano2sec)

        # error is thrown when called with an invalid parameter
        self.assertRaises(TypeError, nano2sec, None)
        self.assertRaises(ValueError, nano2sec, "string")

        # test valid parameters
        self.assertEqual(0.0, nano2sec(0))
        self.assertAlmostEqual(
            Decimal(123.456789123), nano2sec(123456789123), 9
        )
        self.assertAlmostEqual(
            Decimal(0.123456789123), nano2sec(123456789.123), 9
        )
        self.assertAlmostEqual(
            Decimal(-123.456789123), nano2sec(-123456789123), 9
        )
        self.assertAlmostEqual(
            Decimal(123.456789123), nano2sec("123456789123"), 9
        )

    def test_check_file(self):
        """Test check_file()"""
        # function should return false when file doesn't exist
        self.assertFalse(check_file('nofile.csv'))
        self.assertFalse(check_file(''))

        # function should throw an error when no filename is set
        self.assertRaises(TypeError, check_file)

        # function should return true if file exists
        self.assertTrue(check_file(constants.TEST_SAMPLE_TIMESTAMP_FILE))

    def test_file_is_newer(self):
        """Test file_is_newer()"""
        NEWER_FILE = 'newer_file.tmp'

        # create a testfile
        with open(NEWER_FILE, 'w') as outfile:
            outfile.write("test")

        # function should return false when any of the files doesn't exist
        self.assertFalse(file_is_newer('nofile.csv', 'nofile.csv'))
        self.assertFalse(
            file_is_newer('nofile.csv', constants.TEST_SAMPLE_TIMESTAMP_FILE)
        )
        self.assertFalse(
            file_is_newer(constants.TEST_SAMPLE_TIMESTAMP_FILE, 'nofile.csv')
        )

        # function should throw an error when no filename is set
        self.assertRaises(TypeError, file_is_newer)
        self.assertRaises(TypeError, file_is_newer, '')
        self.assertRaises(TypeError, file_is_newer, None, '')

        # function should return false if both files
        # were modified at the same time
        self.assertFalse(file_is_newer(
            constants.TEST_SAMPLE_TIMESTAMP_FILE,
            constants.TEST_SAMPLE_TIMESTAMP_FILE)
        )

        # file 1 is newer than file 2
        self.assertTrue(file_is_newer(
            NEWER_FILE,
            constants.TEST_SAMPLE_TIMESTAMP_FILE)
        )

        # file 1 is older than file 2
        self.assertFalse(file_is_newer(
            constants.TEST_SAMPLE_TIMESTAMP_FILE,
            NEWER_FILE)
        )

    def test_is_dict(self):
        """Test is_dict()"""
        # error is thrown when called without parameters
        self.assertRaises(TypeError, is_dict)

        self.assertFalse(is_dict(None))
        self.assertFalse(is_dict("not_a_dict"))
        self.assertTrue(is_dict({"string": "test"}))

    def test_check_dict(self):
        """Test check_dict()"""
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

        # should return false if parameter is not a list (and name is not set)
        self.assertFalse(check_dict(None))
        self.assertFalse(check_dict("string"))

        # should return true if key is found in dictionary
        self.assertTrue(check_dict({"string": "test"}, "name", "string"))
        self.assertTrue(check_dict(
            {"string": "test", 7: "test"},
            "name",
            list({7, "string"})
        ))

        # should return false if key is not found in dictionary
        self.assertFalse(check_dict(
            {"string": "test"},
            "name",
            list({7})
        ))

    def test_keys_in_dict(self):
        """Test keys_in_dict()"""
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

        # passing something else than a list should return true
        self.assertFalse(keys_in_dict({"string": "test"}, {}))

        # missing keys
        self.assertFalse(keys_in_dict({"string": "test"}, 7))
        self.assertFalse(keys_in_dict({7: "test"}, "string"))
        self.assertFalse(keys_in_dict({"string": "test"}, list({7, "string"})))

    def test_is_list(self):
        """Test is_list()"""
        # error is thrown when called without parameters
        self.assertRaises(TypeError, is_list)

        # error is thrown when called with an invalid parameter
        with self.assertRaises(TypeError) as cm:
            is_list(None, "name")
        self.assertEqual("param name should be a list", str(cm.exception))

        with self.assertRaises(TypeError) as cm:
            is_list("string", "string_name")
        self.assertEqual(
            "param string_name should be a list", str(cm.exception)
        )

        # should return false if parameter is not a list (and name is not set)
        self.assertFalse(is_list(None))
        self.assertFalse(is_list("string"))

        # should return true if parameter is a list
        self.assertTrue(is_list(["string", "test"], "name"))

    def test_is_string(self):
        """Test is_string()"""
        self.assertRaises(TypeError, is_string)

        # error is thrown when called with an invalid parameter
        with self.assertRaises(TypeError) as cm:
            is_string(None, "name")
        self.assertEqual(
            "param name should be a string",
            str(cm.exception)
        )

        # error is thrown when called with an invalid parameter
        with self.assertRaises(TypeError) as cm:
            is_string(123, "name")
        self.assertEqual(
            "param name should be a string",
            str(cm.exception)
        )

        # error is thrown when called with an invalid parameter
        with self.assertRaises(TypeError) as cm:
            is_string({}, "name")
        self.assertEqual(
            "param name should be a string",
            str(cm.exception)
        )

        # error is thrown when called with an invalid parameter
        with self.assertRaises(TypeError) as cm:
            is_string([], "name")
        self.assertEqual(
            "param name should be a string",
            str(cm.exception)
        )

        self.assertFalse(is_string(None))
        self.assertFalse(is_string(None, None))

        self.assertTrue(is_string("string", "name"))

    def test_num_string(self):
        """Test check_num_string()"""
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

        self.assertEqual(0, check_num_string(0, "name"))
        self.assertEqual(1, check_num_string(1, "name"))
        self.assertEqual(-1, check_num_string(-1, "name"))
        self.assertEqual(2, check_num_string(2, "name"))

        self.assertEqual(0, check_num_string("0", "name"))
        self.assertEqual(1, check_num_string("1", "name"))
        self.assertEqual(-1, check_num_string("-1", "name"))
        self.assertEqual(2, check_num_string("2", "name"))

    def test_get_repo_slug(self):
        """Test get_repo_slug()"""
        self.assertEqual(None, get_repo_slug())
        self.assertEqual(None, get_repo_slug("abcd", None))
        self.assertEqual(None, get_repo_slug(None, "efgh"))
        self.assertEqual(None, get_repo_slug(None, None))

        self.assertEqual("abcd/efgh", get_repo_slug("abcd", "efgh"))
        self.assertEqual("Abcd/eFgh", get_repo_slug("Abcd", "eFgh"))
        self.assertEqual("123/456", get_repo_slug(123, 456))
