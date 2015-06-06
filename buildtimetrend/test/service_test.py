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

        self.assertEquals("0.0s", format_duration(0))
        self.assertEquals("1.0s", format_duration(1))
        self.assertEquals("1.6s", format_duration(1.6))
        self.assertEquals("1.6s", format_duration(1.63))
        self.assertEquals("1.7s", format_duration(1.67))

        self.assertEquals("59.7s", format_duration(59.7))
        self.assertEquals("1m 0.0s", format_duration(60))
        self.assertEquals("1m 0.3s", format_duration(60.3))
        self.assertEquals("1m 1.0s", format_duration(61))

        self.assertEquals("59m 59.7s", format_duration(3599.7))
        self.assertEquals("1h 0m 0.0s", format_duration(3600))
        self.assertEquals("1h 0m 0.3s", format_duration(3600.3))
        self.assertEquals("1h 0m 1.0s", format_duration(3601))

        self.assertEquals("2h 5m 0.0s", format_duration(7500))

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
        error_msg = "Error checking if build exists"
        self.assertTrue(
            check_process_parameters("user/repo", 1234) in (None, error_msg)
        )
