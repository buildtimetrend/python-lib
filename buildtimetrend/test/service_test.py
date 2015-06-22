# vim: set expandtab sw=4 ts=4:
"""
Unit tests for Service

Copyright (C) 2014-2015 Dieter Adriaenssens <ruleant@users.sourceforge.net>

This file is part of buildtimetrend/service
<https://github.com/buildtimetrend/service/>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

from buildtimetrend.service import is_repo_allowed
from buildtimetrend.service import format_duration
from buildtimetrend.service import check_process_parameters
from buildtimetrend.service import validate_travis_request
from buildtimetrend.service import validate_task_parameters
from buildtimetrend.settings import Settings
import unittest
import keen


class TestService(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.settings = Settings()

    def setUp(self):
        # reinit settings singleton
        if self.settings is not None:
            self.settings.__init__()

        # reset Keen.io settings
        keen.project_id = None
        keen.write_key = None
        keen.read_key = None
        keen.master_key = None

    def test_is_repo_allowed(self):
        # error is thrown when called without parameters
        self.assertRaises(TypeError, is_repo_allowed)

        # error is thrown when called with an invalid parameter
        self.assertFalse(is_repo_allowed(None))

        # repo is allowed by default
        self.assertTrue(is_repo_allowed("name/repo"))

    def test_is_repo_allowed_set_denied(self):
        # test denied repo
        self.settings.add_setting("denied_repo", {"test1"})

        self.assertTrue(is_repo_allowed("name/repo"))
        self.assertFalse(is_repo_allowed("name/test1"))
        self.assertTrue(is_repo_allowed("name/test2"))

    def test_is_repo_allowed_set_denied_multi(self):
        # test multiple denied repos
        self.settings.add_setting("denied_repo", {"test1", "test2"})

        self.assertTrue(is_repo_allowed("name/repo"))
        self.assertFalse(is_repo_allowed("name/test1"))
        self.assertFalse(is_repo_allowed("name/test2"))

    def test_is_repo_allowed_set_allowed(self):
        # test allowed repo
        self.settings.add_setting("allowed_repo", {"test1"})

        self.assertFalse(is_repo_allowed("name/repo"))
        self.assertTrue(is_repo_allowed("name/test1"))
        self.assertFalse(is_repo_allowed("name/test2"))

    def test_is_repo_allowed_set_allowed_multi(self):
        # test multiple allowed repos
        self.settings.add_setting("allowed_repo", {"test1", "test2"})

        self.assertFalse(is_repo_allowed("name/repo"))
        self.assertTrue(is_repo_allowed("name/test1"))
        self.assertTrue(is_repo_allowed("name/test2"))

    def test_is_repo_allowed_set_denied_allowed(self):
        # set denied repo
        self.settings.add_setting("denied_repo", {"test1"})
        # set allowed repo
        self.settings.add_setting("allowed_repo", {"name"})

        self.assertTrue(is_repo_allowed("name/repo"))
        self.assertFalse(is_repo_allowed("name/test1"))
        self.assertTrue(is_repo_allowed("name/test2"))
        self.assertFalse(is_repo_allowed("owner/repo"))

    def test_format_duration(self):
        # error is thrown when called without parameters
        self.assertRaises(TypeError, format_duration)

        self.assertEquals("unknown", format_duration(None))
        self.assertEquals("unknown", format_duration("string"))
        self.assertEquals("unknown", format_duration(-1))

        self.assertEquals("0s", format_duration(0))
        self.assertEquals("1s", format_duration(1))
        self.assertEquals("1s", format_duration(1.4))
        self.assertEquals("2s", format_duration(1.9))
        self.assertEquals("2s", format_duration(2.1))

        self.assertEquals("59s", format_duration(59.1))
        self.assertEquals("1m 0s", format_duration(59.7))
        self.assertEquals("1m 0s", format_duration(60))
        self.assertEquals("1m 0s", format_duration(60.3))
        self.assertEquals("1m 1s", format_duration(60.6))
        self.assertEquals("1m 1s", format_duration(61))

        self.assertEquals("59m 59s", format_duration(3599.3))
        self.assertEquals("1h 0m 0s", format_duration(3599.7))
        self.assertEquals("1h 0m 0s", format_duration(3600))
        self.assertEquals("1h 0m 0s", format_duration(3600.3))
        self.assertEquals("1h 0m 1s", format_duration(3601))

        self.assertEquals("2h 5m 0s", format_duration(7500))

    def test_check_process_parameters(self):
        # repo or build is not set
        no_repo_build = "Repo or build are not set, format : " \
            "/travis/<repo_owner>/<repo_name>/<build>"

        self.assertEquals(no_repo_build, check_process_parameters())
        self.assertEquals(no_repo_build, check_process_parameters("user/repo"))
        self.assertEquals(no_repo_build, check_process_parameters(None, 1234))

        # repo is not allowed
        # set denied repo
        self.settings.add_setting("denied_repo", {"test1"})
        self.assertEquals(
            "Project 'user/test1' is not allowed.",
            check_process_parameters("user/test1", 1234)
        )

        # Keen.io write key is not set
        self.assertEquals(
            "Keen IO write key not set, no data was sent",
            check_process_parameters("user/repo", 1234)
        )

        # TODO complete test when has_build_id() can be mocked
        # set keen project ID and write key
        keen.project_id = "1234abcd"
        keen.write_key = "1234abcd5678efgh"
        with self.assertRaises(Exception) as exc:
            validate_task_parameters("user/repo", 1234)
        self.assertEqual(
            "Error checking if build exists.", str(exc.exception)
        )

    def test_validate_travis_request(self):
        # repo or build is not set
        no_repo_build = "Repo or build are not set, format : " \
            "/travis/<repo_owner>/<repo_name>/<build>"

        self.assertEquals(no_repo_build, validate_travis_request())
        self.assertEquals(no_repo_build, validate_travis_request("user/repo"))
        self.assertEquals(no_repo_build, validate_travis_request(None, 1234))

        # repo is not allowed
        # set denied repo
        self.settings.add_setting("denied_repo", {"test1"})
        self.assertEquals(
            "Project 'user/test1' is not allowed.",
            validate_travis_request("user/test1", 1234)
        )

    def test_validate_task_parameters(self):
        # Keen.io write key is not set
        self.assertEquals(
            "Keen IO write key not set, no data was sent",
            validate_task_parameters("user/repo", 1234)
        )

        # TODO complete test when has_build_id() can be mocked
        # set keen project ID and write key
        keen.project_id = "1234abcd"
        keen.write_key = "1234abcd5678efgh"
        with self.assertRaises(Exception) as exc:
            validate_task_parameters("user/repo", 1234)
        self.assertEqual(
            "Error checking if build exists.", str(exc.exception)
        )
